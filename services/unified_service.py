from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List, Dict, Any
import base64
import io
import requests
from datetime import datetime, timedelta
import uuid
import asyncio
import logging

# Import UUID service for safe conversion
from services.uuid_service import UUIDService

logger = logging.getLogger(__name__)

from schemas.unified import (
    LoginRequest, LoginResponse,
    DeviceRegisterRequest, DeviceResponse,
    QRCodeResponse,
    UnifiedMessageRequest, UnifiedMessageResponse,
    MessageStatusUpdate,
    GroupInfo, GroupMember,
    WebhookMessage, WebhookStatusUpdate,
    MessageType
)
from models.device import Device, DeviceType
from models.reseller import Reseller
from models.busi_user import BusiUser
from models.message_usage import MessageUsageCreditLog
from models.message import Message, ChannelType, MessageMode, MessageType as ModelMessageType
from services.whatsapp_engine_service import WhatsAppEngineService
from services.message_usage_service import MessageUsageService


class UnifiedWhatsAppService:
    def __init__(self, db: Session):
        self.db = db
        self.engine_service = WhatsAppEngineService(db)
        self.message_usage_service = MessageUsageService(db)

    # Authentication Methods
    def login(self, login_data: LoginRequest) -> LoginResponse:
        """Login to WhatsApp service"""
        try:
            # Find user by phone number
            user = self.db.query(BusiUser).filter(BusiUser.phone == login_data.phone_number).first()
            if not user:
                return LoginResponse(
                    success=False,
                    message="User not found"
                )

            # Get or create device
            device = self._get_or_create_device(user.user_id, login_data.device_id)
            
            # Check device status
            if device.session_status == "connected":
                return LoginResponse(
                    success=True,
                    message="Already logged in",
                    device_id=device.device_id,
                    session_status=device.session_status,
                    access_token=self._generate_access_token(device.device_id)
                )
            else:
                # Generate QR code for new login
                qr_code = self._generate_qr_code(device.device_id)
                device.session_status = "qr_generated"
                device.qr_last_generated = datetime.utcnow()
                self.db.commit()
                
                return LoginResponse(
                    success=True,
                    message="QR code generated. Please scan with WhatsApp.",
                    device_id=device.device_id,
                    qr_code=qr_code,
                    session_status=device.session_status
                )
                
        except Exception as e:
            return LoginResponse(
                success=False,
                message=f"Login failed: {str(e)}"
            )

    def logout(self, user_id: str) -> Dict[str, str]:
        """Logout from WhatsApp service"""
        try:
            devices = self.db.query(Device).filter(Device.user_id == user_id).all()
            for device in devices:
                device.session_status = "disconnected"
                device.last_active = datetime.utcnow()
            
            self.db.commit()
            return {"message": "Logged out successfully"}
        except Exception as e:
            raise Exception(f"Logout failed: {str(e)}")

    # Device Management Methods
    def register_device(self, device_data: DeviceRegisterRequest, user_id: str) -> DeviceResponse:
        """Register new device"""
        try:
            device = Device(
                device_id=str(uuid.uuid4()),
                user_id=user_id,
                device_name=device_data.device_name,
                device_type=device_data.device_type,
                session_status="disconnected",
                created_at=datetime.utcnow()
            )
            
            self.db.add(device)
            self.db.commit()
            
            return DeviceResponse(
                success=True,
                device_id=device.device_id,
                device_name=device.device_name,
                device_type=device.device_type,
                session_status=device.session_status,
                created_at=device.created_at
            )
            
        except Exception as e:
            raise Exception(f"Failed to register device: {str(e)}")

    def delete_device(self, device_id: str, user_id: str) -> None:
        """Delete device"""
        try:
            device = self.db.query(Device).filter(
                Device.device_id == device_id,
                Device.user_id == user_id
            ).first()
            
            if not device:
                raise Exception("Device not found")
            
            self.db.delete(device)
            self.db.commit()
            
        except Exception as e:
            raise Exception(f"Failed to delete device: {str(e)}")

    def generate_qr_code(self, device_id: str, user_id: str) -> QRCodeResponse:
        """Generate QR code for device"""
        try:
            device = self.db.query(Device).filter(
                Device.device_id == device_id,
                Device.user_id == user_id
            ).first()
            
            if not device:
                raise Exception("Device not found")
            
            # Generate new QR code
            qr_code = self._generate_qr_code(device_id)
            device.session_status = "qr_generated"
            device.qr_last_generated = datetime.utcnow()
            self.db.commit()
            
            return QRCodeResponse(
                success=True,
                qr_code=qr_code,
                device_id=device_id,
                qr_last_generated=device.qr_last_generated,
                session_status=device.session_status,
                expires_at=datetime.utcnow() + timedelta(minutes=5)
            )
            
        except Exception as e:
            raise Exception(f"Failed to generate QR code: {str(e)}")

    # Unified Message Methods
    async def send_message(self, device_id: str, to: str, message: str) -> Dict[str, Any]:
        """Send message with comprehensive logging and validation"""
        logger.info(f"🚀 STARTING MESSAGE SEND")
        logger.info(f"   Device ID: {device_id}")
        logger.info(f"   To: {to}")
        logger.info(f"   Message: {message[:100]}...")
        
        try:
            # 1. VALIDATE DEVICE EXISTS
            device = self.db.query(Device).filter(Device.device_id == device_id).first()
            if not device:
                error_msg = f"Device {device_id} not found in database"
                logger.error(f"❌ {error_msg}")
                return {"success": False, "error": error_msg}
            
            logger.info(f"✅ Device found: {device.device_name} (User: {device.busi_user_id}, Type: {device.device_type})")
            
            # 2. ROUTE BY DEVICE TYPE
            if device.device_type == DeviceType.official:
                logger.info(f"🔹 Routing to official WhatsApp Messaging Service...")
                from services.official_public_message_service import OfficialPublicMessageService
                official_service = OfficialPublicMessageService(self.db)
                return await official_service.send_message(
                    device_id=device_id, 
                    phone_number=to, 
                    message=message
                )

            # 3. CHECK REAL DEVICE STATUS IN ENGINE (Unofficial only)
            logger.info(f"🔍 Checking device status in WhatsApp Engine...")
            device_status = self.engine_service.check_device_status(str(device_id))
            actual_status = device_status.get("status")
            
            logger.info(f"   Engine Status: {actual_status}")
            logger.info(f"   Engine Response: {device_status}")
            
            if actual_status != "connected":
                error_msg = f"Device not connected in WhatsApp Engine. Status: {actual_status}"
                logger.error(f"❌ {error_msg}")
                
                # Sync database with engine status
                logger.info(f"🔄 Syncing database status with engine...")
                self.engine_service.sync_device_status(str(device_id))
                
                return {"success": False, "error": error_msg}
            
            logger.info(f"✅ Device is connected in WhatsApp Engine")
            
            # 3. SEND MESSAGE TO ENGINE
            logger.info(f"📤 Sending message to WhatsApp Engine...")
            result = self.engine_service.send_message(
                device_id=str(device_id),
                to=to,
                message=message
            )
            
            logger.info(f"   Engine Result: {result}")
            
            if result.get("success"):
                logger.info(f"✅ Message sent successfully!")
                message_id = result.get('result', {}).get('messageId')
                
                # 🔥 DEDUCT CREDITS
                try:
                    # 4. CREATE DATABASE RECORD
                    from models.message import Message, MessageMode, ChannelType, MessageType as ModelMessageType, MessageStatus
                    real_id = message_id or str(uuid.uuid4())
                    db_message = Message(
                        message_id=real_id,
                        busi_user_id=str(device.busi_user_id),
                        channel=ChannelType.WHATSAPP,
                        mode=MessageMode.UNOFFICIAL,
                        sender_number=str(device.device_id),
                        receiver_number=to,
                        message_type=ModelMessageType.TEXT,
                        message_body=message,
                        status=MessageStatus.SENT,
                        credits_used=1,
                        sent_at=datetime.utcnow(),
                        created_at=datetime.utcnow()
                    )
                    self.db.add(db_message)

                    self.message_usage_service.deduct_credits(
                        busi_user_id=str(device.busi_user_id),
                        message_id=message_id or f"unified-{uuid.uuid4().hex[:8]}",
                        amount=1
                    )
                    self.db.commit()
                except Exception as credit_err:
                    logger.error(f"⚠️ Credit deduction or message logging failed for unified send: {str(credit_err)}")
                
                return {
                    "success": True, 
                    "message_id": message_id,
                    "result": result.get("result")
                }
            else:
                error_msg = result.get("error", "Unknown engine error")
                logger.error(f"❌ Engine failed to send message: {error_msg}")
                
                # Check if device went offline during send
                if "not connected" in error_msg.lower():
                    logger.info(f"🔄 Device may have gone offline, syncing status...")
                    self.engine_service.sync_device_status(str(device_id))
                
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            logger.error(f"❌ EXCEPTION in send_message: {str(e)}")
            logger.error(f"   Exception Type: {type(e).__name__}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return {"success": False, "error": f"Exception: {str(e)}"}

    async def send_media_message(self, device_id: str, to: str, caption: str, media_url: str, media_type: str = "image") -> Dict[str, Any]:
        """Send media message via engine service"""
        logger.info(f"📤 Sending {media_type} message to {to} via device {device_id}")
        try:
            # 1. VALIDATE DEVICE EXISTS
            device = self.db.query(Device).filter(Device.device_id == device_id).first()
            if not device:
                return {"success": False, "error": f"Device {device_id} not found"}
            
            # ROUTE BY DEVICE TYPE
            if device.device_type == DeviceType.official:
                logger.info(f"🔹 Routing media message to official WhatsApp Messaging Service...")
                from services.official_public_message_service import OfficialPublicMessageService
                official_service = OfficialPublicMessageService(self.db)
                return await official_service.send_media(
                    device_id=device_id, 
                    phone_number=to, 
                    media_url=media_url, 
                    caption=caption
                )

            # 2. SEND TO ENGINE (Unofficial)
            # We use send_file_with_caption which handles URL or local path
            # The engine service handles the HTTP call to /session/:id/file-caption
            result = self.engine_service.send_file_with_caption(
                device_id=str(device_id),
                to=to,
                file_path=media_url,
                caption=caption,
                device_name=device.device_name
            )
            
            logger.info(f"   Media Engine Result: {result}")
            
            if result.get("success"):
                # 🔥 DEDUCT CREDITS & LOG MESSAGE
                try:
                    message_id = result.get('data', {}).get('messageId') or f"media-{uuid.uuid4().hex[:8]}"
                    
                    # CREATE DATABASE RECORD
                    from models.message import Message, MessageMode, ChannelType, MessageType as ModelMessageType, MessageStatus
                    db_message = Message(
                        message_id=message_id,
                        busi_user_id=str(device.busi_user_id),
                        channel=ChannelType.WHATSAPP,
                        mode=MessageMode.UNOFFICIAL,
                        sender_number=str(device.device_id),
                        receiver_number=to,
                        message_type=ModelMessageType.MEDIA,
                        message_body=caption or "[Media Message]",
                        status=MessageStatus.SENT,
                        credits_used=1,
                        sent_at=datetime.utcnow(),
                        created_at=datetime.utcnow()
                    )
                    self.db.add(db_message)

                    self.message_usage_service.deduct_credits(
                        busi_user_id=str(device.busi_user_id),
                        message_id=message_id
                    )
                    self.db.commit()
                except Exception as credit_err:
                    logger.error(f"⚠️ Credit deduction or message logging failed for unified media send: {str(credit_err)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Exception in send_media_message: {str(e)}")
            return {"success": False, "error": str(e)}
    def send_unified_message(self, message_data: UnifiedMessageRequest) -> UnifiedMessageResponse:
        """Send unified message with enhanced engine validation and error handling"""
        
        logger.info(f"Starting unified message send for device {message_data.device_id} to {message_data.to}")
        
        # 1. GET DEVICE
        device = self.db.query(Device).filter(Device.device_id == message_data.device_id).first()
        if not device:
            raise Exception(f"Device {message_data.device_id} not found")
        
        # 2. VALIDATE PHONE NUMBER
        receiver = message_data.to.strip()
        if not receiver or len(receiver) < 5:
            raise Exception(f"Invalid receiver number: {receiver}")
        
        if len(receiver) > 50:
            logger.warning(f"Receiver number too long: {receiver}. Truncating.")
        # --- [CREDIT CHECK & DEDUCTION] ---
        # 🔥 FIXED: Dynamically calculate rate based on plan
        credits_to_deduct = self.message_usage_service.get_deduction_rate(message_data.user_id)
        
        # 3. CREATE MESSAGE RECORD
        message = Message(
            message_id=str(uuid.uuid4()),
            busi_user_id=message_data.user_id,
            channel=ChannelType.WHATSAPP,
            mode=MessageMode.UNOFFICIAL,
            sender_number=device.device_id,
            receiver_number=receiver,
            message_body=self._build_message_body(message_data),
            message_type=message_data.type.upper(),
            status="PENDING",
            credits_used=credits_to_deduct,
            created_at=datetime.utcnow()
        )
        
        try:
            self.db.add(message)
            self.db.flush()

            # Deduct credits upfront (will be refunded if send fails)
            try:
                self.message_usage_service.deduct_credits(
                    busi_user_id=message_data.user_id,
                    message_id=message.message_id,
                    amount=credits_to_deduct
                )
            except Exception as e:
                logger.error(f"Credit deduction failed: {str(e)}")
                raise e

            # 4. SEND TO WHATSAPP ENGINE
            logger.info(f"Sending message via engine service - Device: {device.device_id}, To: {receiver}")
            
            result = self.engine_service.send_message(
                device_id=str(device.device_id),
                to=receiver,
                message=message.message_body,
                skip_report=True # 🔥 PREVENT DUPLICATE LOGGING
            )
            
            if result["success"]:
                message.status = "SENT"
                message.sent_at = datetime.utcnow()
                
                # Update Message ID if Baileys provided one
                if result.get("result") and result["result"].get("messageId"):
                    message.message_id = result["result"]["messageId"]
                elif result.get("data") and result["data"].get("messageId"):
                    message.message_id = result["data"]["messageId"]
                
                logger.info(f"Message sent successfully to {receiver} via device {device.device_id}")
            else:
                message.status = "FAILED"
                # 🔥 REFUND CREDITS if engine failed to accept
                try:
                    # To refund, we add negative deduction
                    # Fetch user again to get current balance for logging
                    user = self.db.query(BusiUser).filter(BusiUser.busi_user_id == message_data.user_id).first()
                    is_res = False
                    if not user:
                        user = self.db.query(Reseller).filter(Reseller.reseller_id == message_data.user_id).first()
                        is_res = True
                    
                    if user:
                        if not is_res:
                            user.credits_remaining += credits_to_deduct
                            user.credits_used -= credits_to_deduct
                            new_bal = user.credits_remaining
                        else:
                            user.available_credits += credits_to_deduct
                            user.used_credits -= credits_to_deduct
                            new_bal = user.available_credits
                        
                        refund_log = MessageUsageCreditLog(
                            usage_id=f"refund-{uuid.uuid4().hex[:8]}",
                            busi_user_id=message_data.user_id,
                            message_id=message.message_id,
                            credits_deducted=-credits_to_deduct,
                            balance_after=new_bal,
                            timestamp=datetime.utcnow()
                        )
                        self.db.add(refund_log)
                        logger.info(f"💰 REFUNDED {credits_to_deduct} credits to {message_data.user_id}")
                except Exception as refund_err:
                    logger.error(f"❌ REFUND FAILED: {str(refund_err)}")
                
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Engine send failed for device {device.device_id}: {error_msg}")
                raise Exception(f"WhatsApp Engine error: {error_msg}")
            
            # 5. COMMIT TRANSACTION
            self.db.commit()
            
            return UnifiedMessageResponse(
                success=True,
                message_id=str(message.message_id),
                status=message.status,
                recipient=receiver,
                is_group=message_data.is_group,
                message_type=message_data.type,
                sent_at=message.sent_at,
                credits_used=message.credits_used
            )
            
        except Exception as e:
            # 9. ROLLBACK ON ERROR
            try:
                self.db.rollback()
                message.status = "FAILED"
                self.db.commit()
            except Exception as inner_e:
                logger.error(f"Secondary rollback error: {inner_e}")
                self.db.rollback()
            
            logger.error(f"Failed to send message to {receiver}: {e}")
            raise Exception(f"Failed to send message: {str(e)}")

    def get_message_status(self, message_id: str, user_id: str) -> Dict[str, Any]:
        """Get message status and details"""
        try:
            message = self.db.query(Message).filter(
                Message.message_id == message_id,
                Message.user_id == user_id
            ).first()
            
            if not message:
                raise Exception("Message not found")
            
            return {
                "message_id": message.message_id,
                "status": message.status,
                "receiver_number": message.receiver_number,
                "message_body": message.message_body,
                "message_type": message.message_type,
                "credits_used": message.credits_used,
                "created_at": message.created_at,
                "sent_at": message.sent_at,
                "updated_at": message.updated_at
            }
            
        except Exception as e:
            raise Exception(f"Failed to get message status: {str(e)}")

    def update_message_status(self, message_id: str, status_update: MessageStatusUpdate) -> Dict[str, str]:
        """Update message status"""
        try:
            message = self.db.query(Message).filter(Message.message_id == message_id).first()
            
            if not message:
                raise Exception("Message not found")
            
            message.status = status_update.status
            message.updated_at = datetime.utcnow()
            
            if status_update.delivered_at:
                message.sent_at = status_update.delivered_at
            if status_update.read_at:
                message.updated_at = status_update.read_at
            
            self.db.commit()
            
            return {"message": "Message status updated successfully", "status": status_update.status}
            
        except Exception as e:
            raise Exception(f"Failed to update message status: {str(e)}")

    # Group Management Methods
    def get_groups(self, user_id: str) -> List[GroupInfo]:
        """Get all WhatsApp groups for user"""
        try:
            # Simulate group data - in real implementation, fetch from WhatsApp API
            groups = [
                GroupInfo(
                    group_id="group1",
                    group_name="Family Group",
                    participant_count=15,
                    is_admin=True,
                    created_at=datetime.utcnow() - timedelta(days=30)
                ),
                GroupInfo(
                    group_id="group2",
                    group_name="Work Team",
                    participant_count=25,
                    is_admin=False,
                    created_at=datetime.utcnow() - timedelta(days=15)
                )
            ]
            return groups
        except Exception as e:
            raise Exception(f"Failed to get groups: {str(e)}")

    def get_group_members(self, group_id: str, user_id: str) -> List[GroupMember]:
        """Get all members of a specific group"""
        try:
            # Simulate group members data
            members = [
                GroupMember(
                    phone_number="+919876543210",
                    name="John Doe",
                    is_admin=True,
                    joined_at=datetime.utcnow() - timedelta(days=30)
                ),
                GroupMember(
                    phone_number="+919876543211",
                    name="Jane Smith",
                    is_admin=False,
                    joined_at=datetime.utcnow() - timedelta(days=25)
                )
            ]
            return members
        except Exception as e:
            raise Exception(f"Failed to get group members: {str(e)}")

    # Webhook Methods
    def process_webhook_message(self, webhook_data: WebhookMessage) -> Dict[str, str]:
        """Process incoming webhook message"""
        try:
            # Store incoming message
            message = Message(
                message_id=webhook_data.message_id,
                user_id=self._get_user_by_device(webhook_data.device_id),
                receiver_number=webhook_data.from_number,
                message_body=webhook_data.message_content,
                message_type=webhook_data.message_type.upper(),
                status=webhook_data.status,
                created_at=webhook_data.timestamp
            )
            
            self.db.add(message)
            self.db.commit()
            
            return {"message": "Webhook processed successfully"}
            
        except Exception as e:
            raise Exception(f"Failed to process webhook: {str(e)}")

    def process_webhook_status_update(self, webhook_data: WebhookStatusUpdate) -> Dict[str, str]:
        """Process webhook status update"""
        try:
            message = self.db.query(Message).filter(Message.message_id == webhook_data.message_id).first()
            
            if message:
                message.status = webhook_data.status
                message.updated_at = webhook_data.timestamp
                self.db.commit()
            
            return {"message": "Status update processed successfully"}
            
        except Exception as e:
            raise Exception(f"Failed to process status update: {str(e)}")

    # Helper Methods
    def _get_active_device(self, user_id: str, device_id: Optional[str] = None) -> Optional[Device]:
        """Get active device for user"""
        query = self.db.query(Device).filter(Device.user_id == user_id)
        
        if device_id:
            # ✅ Convert string UUID to UUID object before query
            device_uuid = UUIDService.safe_convert(device_id)
            query = query.filter(Device.device_id == device_uuid)
        
        return query.filter(Device.session_status == "connected").first()

    def _get_or_create_device(self, user_id: str, device_id: Optional[str]) -> Device:
        """Get existing device or create new one"""
        if device_id:
            # ✅ Convert string UUID to UUID object before query
            device_uuid = UUIDService.safe_convert(device_id)
            device = self.db.query(Device).filter(
                Device.device_id == device_uuid,
                Device.user_id == user_id
            ).first()
            if device:
                return device
        
        # Create new device
        device = Device(
            device_id=str(uuid.uuid4()),
            user_id=user_id,
            device_name="Default Device",
            device_type=DeviceType.UNOFFICIAL,  # 🔥 FIXED: Unified service creates UNOFFICIAL devices
            session_status="disconnected",
            created_at=datetime.utcnow()
        )
        
        self.db.add(device)
        self.db.commit()
        return device

    def _build_message_body(self, message_data: UnifiedMessageRequest) -> str:
        """Build message body based on type"""
        if message_data.type == MessageType.TEXT:
            return message_data.message or ""
        elif message_data.caption:
            return message_data.caption
        elif message_data.message:
            return message_data.message
        else:
            return "[Media Message]"

    def _process_base64_file(self, base64_data: str, message_id: str) -> tuple:
        """Process base64 file and return file info"""
        try:
            # Decode base64
            file_content = base64.b64decode(base64_data)
            file_size = len(file_content)
            
            # Save file (in real implementation, save to storage)
            file_url = f"/files/{message_id}"
            file_name = f"media_{message_id}.dat"
            
            return file_url, file_name, file_size
        except Exception:
            return None, None, None

    def _process_media_url(self, media_url: str) -> tuple:
        """Process media URL and return file info"""
        try:
            # Download file (in real implementation)
            response = requests.get(media_url)
            file_size = len(response.content)
            file_name = media_url.split("/")[-1]
            
            return media_url, file_name, file_size
        except Exception:
            return media_url, None, None

    def _generate_qr_code(self, device_id: str) -> str:
        """Generate QR code (simulated)"""
        qr_data = f"whatsapp_qr_{device_id}_{datetime.utcnow().timestamp()}"
        return base64.b64encode(qr_data.encode()).decode()

    def _generate_access_token(self, device_id: str) -> str:
        """Generate access token for device"""
        token_data = f"device_{device_id}_{datetime.utcnow().timestamp()}"
        return base64.b64encode(token_data.encode()).decode()

    def _get_user_by_device(self, device_id: str) -> str:
        """Get user ID by device ID"""
        device = self.db.query(Device).filter(Device.device_id == device_id).first()
        return device.busi_user_id if device else ""

    def check_engine_reachable(self) -> bool:
        """Check if WhatsApp Engine socket is reachable (not health, just connectivity)"""
        return self.engine_service.check_engine_reachable()

    def check_engine_health(self) -> bool:
        """Check if WhatsApp Engine is healthy (strict health check)"""
        health_result = self.engine_service.check_engine_health()
        return health_result["healthy"]

    async def check_device_health(self, device_id: str) -> bool:
        """Check if device is healthy"""
        device_status = self.engine_service.check_device_status(str(device_id))
        return device_status.get("status") == "connected"

    def sync_device_status(self, device_id: str) -> bool:
        """Sync device status with WhatsApp Engine and update DB"""
        return self.engine_service.sync_device_status(str(device_id))
