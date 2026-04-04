import asyncio
import logging
import random
import traceback
import uuid
from sqlalchemy.orm import Session

from core.config import settings
from core.campaign_state import campaign_tracker
from db.db_session import SessionLocal
from models.campaign import Campaign, CampaignStatus, MessageLog
from models.device import Device
from services.unified_service import UnifiedWhatsAppService
from workers.worker_manager import unregister_worker

logger = logging.getLogger("CAMPAIGN_WORKER")

async def campaign_worker(campaign_id: str):
    """
    Independent worker task for a specific campaign.
    Ensures DB session isolation by creating and closing sessions inside the loop.
    """
    worker_id = str(uuid.uuid4())
    logger.info(f"🚀 Worker {worker_id} started for campaign {campaign_id}")

    try:
        while True:
            # 1. Create a fresh session for this iteration
            db = SessionLocal()
            try:
                # Refresh campaign and tracker status from DB/InMemory
                tracker = campaign_tracker.get(campaign_id)
                if not tracker:
                    logger.warning(f"No tracker found for campaign {campaign_id}. Worker exiting.")
                    break

                # Check if campaign is PAUSED or stopped
                if tracker["status"] == CampaignStatus.PAUSED.value:
                    logger.info(f"⏹️ Campaign {campaign_id} PAUSED. Worker stopping.")
                    break
                
                if tracker["status"] in [CampaignStatus.COMPLETED.value, CampaignStatus.FAILED.value]:
                    logger.info(f"✅ Campaign {campaign_id} already {tracker['status']}. Worker exiting.")
                    break

                # Fetch static campaign details needed for this iteration
                campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
                if not campaign:
                    logger.error(f"Campaign {campaign_id} not found in DB.")
                    break

                # Dequeue next recipient
                if not tracker.get("recipients"):
                    # Double check if we should be COMPLETED
                    campaign.status = CampaignStatus.COMPLETED
                    db.commit()
                    tracker["status"] = CampaignStatus.COMPLETED.value
                    logger.info(f"✅ Campaign {campaign_id} finished all recipients.")
                    break

                recipient_data = tracker["recipients"].pop(0)
                tracker["remaining"] = len(tracker["recipients"])
                
                phone = recipient_data.get("phone")
                row_data = recipient_data.get("row_data", {})
                
                if not phone:
                    continue

                # Prepare devices and templates (Round Robin style based on count)
                # Note: We fetch these from campaign relationship which is now session-bound
                devices = [cd.device for cd in campaign.devices if cd.device]
                templates = list(campaign.templates)

                if not devices or not templates:
                    logger.error(f"Campaign {campaign_id} lacks devices or templates.")
                    tracker["status"] = CampaignStatus.FAILED.value
                    campaign.status = CampaignStatus.FAILED
                    db.commit()
                    break

                sent_so_far = campaign.sent_count + campaign.failed_count
                device = devices[sent_so_far % len(devices)]
                template = templates[sent_so_far % len(templates)]

                # Content formatting
                content = template.content
                for key, val in row_data.items():
                    content = content.replace(f"{{{key}}}", str(val))

                # Rate limiting / Delay
                delay = template.delay_override
                if delay is None:
                    is_warm = getattr(device, 'warm_status', False)
                    delay = random.randint(settings.WARM_MIN_DELAY, settings.WARM_MAX_DELAY) if is_warm else random.randint(settings.MIN_DELAY, settings.MAX_DELAY)
                
                actual_delay = max(0.5, delay)
                await asyncio.sleep(actual_delay)

                # Send Message
                success = False
                error_msg = None
                
                media_url = campaign.media_url or template.media_url
                media_type = campaign.media_type or (template.media_type or "image")
                
                unified_service = UnifiedWhatsAppService(db)
                try:
                    if media_url:
                        result = await unified_service.send_media_message(
                            device_id=str(device.device_id),
                            to=phone,
                            caption=content,
                            media_url=media_url,
                            media_type=media_type
                        )
                    else:
                        result = await unified_service.send_message(
                            device_id=str(device.device_id),
                            to=phone,
                            message=content
                        )
                    
                    if result and result.get("success"):
                        success = True
                        campaign.sent_count += 1
                    else:
                        error_msg = result.get("error", "Unknown error") if result else "No response"
                        campaign.failed_count += 1
                except Exception as e:
                    error_msg = str(e)
                    campaign.failed_count += 1
                    logger.error(f"Error sending message to {phone}: {e}")

                # Log Result
                log_entry = MessageLog(
                    campaign_id=campaign_id,
                    device_id=device.device_id,
                    recipient=phone,
                    template_id=template.id,
                    status="success" if success else f"failed: {error_msg}",
                    retry_count=0,
                    response_time=int(actual_delay * 1000)
                )
                db.add(log_entry)
                
                # Commit iteration
                db.commit()
                logger.info(f"📊 Campaign {campaign_id}: {phone} -> {'✅' if success else '❌'}")

            except Exception as e:
                logger.error(f"Error in worker loop iteration: {e}")
                db.rollback()
            finally:
                # 2. ALWAYS close the session at the end of iteration
                db.close()

            # yield control back to event loop
            await asyncio.sleep(0.01)

    except asyncio.CancelledError:
        logger.info(f"🛑 Worker {worker_id} for campaign {campaign_id} CANCELLED")
    except Exception as e:
        logger.error(f"🔥 Worker {worker_id} CRASHED: {e}\n{traceback.format_exc()}")
    finally:
        # Cleanup Registry
        await unregister_worker(campaign_id)
        logger.info(f"🏁 Worker {worker_id} for campaign {campaign_id} STOPPED")
