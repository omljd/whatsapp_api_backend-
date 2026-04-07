import asyncio
import json
import logging
import traceback
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from core.config import settings
from core.campaign_state import campaign_tracker
from models.campaign import Campaign, CampaignDevice, MessageTemplate, MessageLog, CampaignStatus
from models.device import Device
from schemas.campaign import CampaignCreateRequest, CampaignResponse
from workers.bulk_messaging_worker import campaign_worker
from workers.worker_manager import is_worker_active, register_worker

logger = logging.getLogger("CAMPAIGN_SERVICE")

class CampaignService:
    def __init__(self, db: Session):
        self.db = db

    def create_campaign(self, user_id: str, request_data: CampaignCreateRequest) -> Campaign:
        try:
            # Check max devices validation
            if len(request_data.device_ids) > 5:
                raise HTTPException(status_code=400, detail="Maximum 5 devices allowed per campaign")
            
            # Check user owns devices
            for device_id in request_data.device_ids:
                device = self.db.query(Device).filter(Device.device_id == device_id, Device.busi_user_id == user_id, Device.is_active == True).first()
                if not device:
                    raise HTTPException(status_code=400, detail=f"Device {device_id} not found or unauthorized")

            # Create Campaign
            campaign = Campaign(
                busi_user_id=user_id,
                sheet_id=request_data.sheet_id,
                source_file_url=request_data.source_file_url, # 🔥 NEW
                name=request_data.name,
                status=CampaignStatus.PENDING,
                media_url=request_data.media_url,
                media_type=request_data.media_type
            )
            self.db.add(campaign)
            self.db.flush()

            # Add Devices
            for device_id in request_data.device_ids:
                cd = CampaignDevice(campaign_id=campaign.id, device_id=device_id)
                self.db.add(cd)

            # Add Templates
            for t in request_data.templates:
                mt = MessageTemplate(
                    campaign_id=campaign.id, 
                    content=t.content, 
                    media_url=t.media_url,
                    media_type=t.media_type,
                    delay_override=t.delay_override
                )
                self.db.add(mt)

            self.db.commit()
            self.db.refresh(campaign)
            return campaign
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def start_campaign(self, user_id: str, campaign_id: str, rows_data: List[Dict[str, Any]]):
        """
        Start a campaign: process rows directly, set status to running, spawn worker task.
        Uses worker_manager for concurrency control.
        """
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.busi_user_id == user_id).first()
            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")

            if campaign.status not in [CampaignStatus.PENDING, CampaignStatus.PAUSED]:
                raise HTTPException(status_code=400, detail=f"Cannot start campaign in state {campaign.status.value}")

            # 1. Check if worker is already active via worker_manager
            if await is_worker_active(str(campaign_id)):
                logger.info(f"Campaign {campaign_id} already has an active worker task.")
                # Ensure DB status is synced if tracker/registry says it's running
                if campaign.status != CampaignStatus.RUNNING:
                    campaign.status = CampaignStatus.RUNNING
                    self.db.commit()
                return {"status": "success", "message": "Campaign is already running."}

            # 2. Prepare recipients if Pending
            if campaign.status == CampaignStatus.PENDING:
                limit = settings.SESSION_MESSAGE_LIMIT
                process_rows = rows_data[:limit]
                campaign.total_recipients = len(process_rows)
                
                campaign_tracker[str(campaign_id)] = {
                    "status": CampaignStatus.RUNNING.value,
                    "remaining": len(process_rows),
                    "total": len(process_rows),
                    "recipients": process_rows
                }
                logger.info(f"Prepared {len(process_rows)} recipients for campaign {campaign_id}")
            else:
                # Resuming
                if str(campaign_id) in campaign_tracker:
                    campaign_tracker[str(campaign_id)]["status"] = CampaignStatus.RUNNING.value
                else:
                    return {"status": "error", "message": "Campaign tracker lost. Please restart campaign."}

            campaign.status = CampaignStatus.RUNNING
            self.db.commit()

            # 3. Start background worker task and register it
            task = asyncio.create_task(campaign_worker(str(campaign.id)))
            await register_worker(str(campaign_id), task)

            return {"status": "success", "message": "Campaign started"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in start_campaign: {e}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Failed to start campaign: {str(e)}")

    async def pause_campaign(self, user_id: str, campaign_id: str):
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.busi_user_id == user_id).first()
            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")

            campaign.status = CampaignStatus.PAUSED
            self.db.commit()
            
            # Update tracker - worker will detect this and stop
            if str(campaign_id) in campaign_tracker:
                campaign_tracker[str(campaign_id)]["status"] = CampaignStatus.PAUSED.value
            
            return {"status": "success", "message": "Campaign paused. Worker will stop shortly."}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error pausing campaign {campaign_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def resume_campaign(self, user_id: str, campaign_id: str):
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.busi_user_id == user_id).first()
            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")

            if campaign.status != CampaignStatus.PAUSED:
                raise HTTPException(status_code=400, detail="Campaign is not paused")

            # Update tracker status first
            if str(campaign_id) in campaign_tracker:
                campaign_tracker[str(campaign_id)]["status"] = CampaignStatus.RUNNING.value
            else:
                return {"status": "error", "message": "Campaign tracker lost. Cannot resume."}

            campaign.status = CampaignStatus.RUNNING
            self.db.commit()

            # Re-spawn task if not already active
            if not await is_worker_active(str(campaign_id)):
                task = asyncio.create_task(campaign_worker(str(campaign.id)))
                await register_worker(str(campaign_id), task)
            
            return {"status": "success", "message": "Campaign resumed"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error resuming campaign {campaign_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_campaign_status(self, user_id: str, campaign_id: str):
        """
        Get real-time tracking of campaign from DB and InMemory state
        """
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.busi_user_id == user_id).first()
            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")

            status = campaign.status.value if hasattr(campaign.status, 'value') else campaign.status
            total_recipients = campaign.total_recipients
            sent_count = campaign.sent_count
            failed_count = campaign.failed_count
            
            remaining = 0
            tracker = campaign_tracker.get(str(campaign_id))
            if tracker:
                remaining = tracker.get("remaining", 0)
                # Use tracker status if it's more up-to-date
                tracker_status = tracker.get("status")
                if tracker_status:
                    status = tracker_status

            return {
                "campaign_id": str(campaign.id),
                "status": status,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "total_recipients": total_recipients,
                "remaining": remaining
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching campaign status: {e}")
            raise HTTPException(status_code=500, detail="Internal server error fetching status")
