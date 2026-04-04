#!/usr/bin/env python3
"""
🔧 PRODUCTION-GRADE FIX (VERY IMPORTANT)
You MUST update backend logic:
Rule:

If device exists in engine AND user is authenticated
→ auto-link device to user in DB

Pseudo-code:
if engine_device_exists and not db_device:
    create_device_for_user()

This prevents this bug forever.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
import requests
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from models.device import Device, DeviceType, SessionStatus
from services.session_validation_service import session_validation_service
from core.config import settings

logger = logging.getLogger(__name__)

class DeviceSyncService:
    """
    🔥 PRODUCTION-GRADE DEVICE SYNC SERVICE
    
    Ensures database is always in sync with WhatsApp Engine
    Auto-creates missing devices for authenticated users
    """
    
    def __init__(self, engine_url: str = None):
        self.engine_url = engine_url or settings.WHATSAPP_ENGINE_BASE_URL
        
    def _is_valid_uuid(self, device_id: str) -> bool:
        """Check if device_id is a valid UUID"""
        try:
            uuid.UUID(device_id)
            return True
        except (ValueError, AttributeError):
            return False
        
    def get_engine_devices(self) -> List[Dict[str, any]]:
        """
        Fetch all devices from WhatsApp Engine
        """
        try:
            # Try the correct endpoint first
            response = requests.get(f"{self.engine_url}/sessions", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                devices = []
                
                # Handle both formats: {device_id: session_info} or [{session_info}]
                if isinstance(data, dict):
                    for device_id, session_info in data.items():
                        # 🔥 SESSION VALIDATION: Filter invalid sessions
                        if not session_validation_service.is_valid_device_id(device_id):
                            logger.warning(f"🗑️ Skipping invalid device_id from engine: {device_id}")
                            continue
                        
                        devices.append({
                            "device_id": device_id,
                            "status": session_info.get("status", "unknown"),
                            "phone": session_info.get("phone", ""),
                            "name": session_info.get("name", f"Device {device_id[:8]}"),
                            "platform": session_info.get("platform", "web")
                        })
                elif isinstance(data, list):
                    for session_info in data:
                        if "id" in session_info:
                            device_id = session_info["id"]
                            
                            # 🔥 SESSION VALIDATION: Filter invalid sessions
                            if not session_validation_service.is_valid_device_id(device_id):
                                logger.warning(f"🗑️ Skipping invalid device_id from engine: {device_id}")
                                continue
                            
                            devices.append({
                                "device_id": device_id,
                                "status": session_info.get("status", "unknown"),
                                "phone": session_info.get("phone", ""),
                                "name": session_info.get("name", f"Device {device_id[:8]}"),
                                "platform": session_info.get("platform", "web")
                            })
                
                return devices
            else:
                logger.error(f"Failed to fetch devices from Engine: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching devices from Engine: {e}")
            return []
    
    def sync_user_devices(self, db: Session, user_id: str) -> Dict[str, any]:
        """
        🔥 CORE SYNC LOGIC
        
        If device exists in engine AND user is authenticated
        → auto-link device to user in DB
        
        This prevents this bug forever.
        """
        logger.info(f"🔄 SYNCING DEVICES FOR USER: {user_id}")
        
        try:
            # Validate user_id is UUID
            try:
                uuid.UUID(user_id)
            except ValueError:
                logger.error(f"❌ Invalid user_id UUID: {user_id}")
                return {"success": False, "error": "Invalid user_id format"}
            
            # Get all devices from Engine
            engine_devices = self.get_engine_devices()
            
            if not engine_devices:
                logger.warning("No devices found in Engine")
                return {"success": False, "error": "No devices in Engine"}
            
            # Get existing devices for this user from DB
            existing_db_devices = db.query(Device).filter(Device.busi_user_id == user_id).all()
            existing_device_ids = {str(device.device_id) for device in existing_db_devices}
            
            logger.info(f"   Engine devices: {len(engine_devices)}")
            logger.info(f"   DB devices for user: {len(existing_db_devices)}")
            
            synced_devices = []
            created_devices = []
            updated_devices = []
            
            for engine_device in engine_devices:
                device_id = engine_device["device_id"]
                
                # 🔥 CRITICAL FIX: Validate and convert device_id to UUID
                try:
                    uuid.UUID(device_id)
                    device_uuid = device_id
                except ValueError:
                    # Invalid UUID - skip this device or generate new UUID
                    logger.warning(f"⚠️ Skipping invalid device_id UUID: {device_id}")
                    continue
                
                # 🔥 PRODUCTION-GRADE FIX: Auto-link device to user
                if device_uuid not in existing_device_ids:
                    # Device exists in Engine but not in DB → Auto-create!
                    logger.info(f"   🆕 Auto-creating device: {device_id}")
                    
                    try:
                        new_device = Device(
                            device_id=device_uuid,
                            busi_user_id=user_id,
                            device_name=engine_device.get("name", f"Device {device_uuid[:8]}"),
                            device_type=DeviceType.web if engine_device.get("platform") == "web" else DeviceType.mobile,
                            session_status=SessionStatus.connected if engine_device.get("status") == "connected" else SessionStatus.disconnected,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        
                        db.add(new_device)
                        db.flush()  # Validate without committing
                        created_devices.append(device_uuid)
                        logger.info(f"   ✅ Created device: {device_uuid} → user: {user_id}")
                        
                    except Exception as create_error:
                        logger.error(f"   ❌ Failed to create device {device_uuid}: {create_error}")
                        db.rollback()
                        continue
                    
                else:
                    # Device exists in both → Update status
                    db_device = next((d for d in existing_db_devices if str(d.device_id) == device_uuid), None)
                    
                    if db_device:
                        # Update session status to match Engine
                        engine_status = engine_device.get("status", "unknown")
                        new_session_status = SessionStatus.connected if engine_status == "connected" else SessionStatus.disconnected
                        
                        # IMPORTANT: Do NOT set unofficial devices to disconnected based on engine heartbeat
                        # Only allow explicit logout/delete to change status
                        is_unofficial = "official whatsapp" not in db_device.device_name.lower()
                        if is_unofficial and db_device.session_status == SessionStatus.connected:
                            logger.info(f"   🛡️ Protected unofficial device {device_id} from auto-disconnect")
                            continue
                        
                        if db_device.session_status != new_session_status:
                            db_device.session_status = new_session_status
                            db_device.updated_at = datetime.utcnow()
                            updated_devices.append(device_uuid)
                            logger.info(f"   🔄 Updated device status: {device_uuid} → {new_session_status}")
                
                synced_devices.append(device_uuid)
            
            # Commit all changes
            db.commit()
            
            # Disable stale devices (exist in DB but not in Engine)
            stale_devices = []
            for db_device in existing_db_devices:
                if str(db_device.device_id) not in [d["device_id"] for d in engine_devices if self._is_valid_uuid(d["device_id"])]:
                    db_device.session_status = SessionStatus.expired
                    stale_devices.append(str(db_device.device_id))
            
            if stale_devices:
                db.commit()
                logger.info(f"   🗑️  Marked {len(stale_devices)} stale devices as expired")
            
            result = {
                "success": True,
                "synced": len(synced_devices),
                "created": len(created_devices),
                "updated": len(updated_devices),
                "stale": len(stale_devices),
                "devices": synced_devices
            }
            
            logger.info(f"🏁 SYNC COMPLETE: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Device sync error: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def ensure_device_exists(self, db: Session, user_id: str, device_id: str) -> Dict[str, any]:
        """
        Ensure a specific device exists for a user
        Auto-create if missing (production-grade fix)
        """
        logger.info(f"🔍 ENSURING DEVICE EXISTS: {device_id} for user {user_id}")
        
        try:
            # Check if device exists in DB for this user
            # For official WhatsApp configs, device_id might be a string phone_number_id
            # We need to handle both UUID and string device_ids
            db_device = None
            
            # 🔥 BYPASS SQLAlchemy ORM type system entirely - use raw SQL to avoid UUID/VARCHAR mismatch
            from sqlalchemy import text
            device_id_str = str(device_id)
            user_id_str = str(user_id)
            
            result = db.execute(
                text("SELECT * FROM devices WHERE device_id::text = :did AND busi_user_id::text = :uid LIMIT 1"),
                {"did": device_id_str, "uid": user_id_str}
            ).fetchone()
            
            if result:
                # Map raw result back to Device ORM object
                db_device = db.query(Device).get(device_id_str)
                if not db_device:
                    # Fallback: try getting by raw string match
                    db_device = db.query(Device).filter(
                        text("device_id::text = :did")
                    ).params(did=device_id_str).first()
            
            if db_device:
                logger.info(f"   ✅ Device exists in DB: {device_id}")
                return {"success": True, "device": db_device, "action": "found"}
            
            # Check if this is an official WhatsApp phone_number_id
            from models.official_whatsapp_config import OfficialWhatsAppConfig
            official_config = db.query(OfficialWhatsAppConfig).filter(
                OfficialWhatsAppConfig.phone_number_id == device_id,
                OfficialWhatsAppConfig.busi_user_id == user_id
            ).first()
            
            if official_config:
                logger.info(f"   📱 Creating Device record for Official WhatsApp config: {device_id}")
                
                # Try to use device_id as UUID, fallback to string if invalid
                try:
                    import uuid
                    uuid.UUID(device_id)
                    # Valid UUID, use as-is
                    device_uuid = device_id
                except (ValueError, AttributeError):
                    # Invalid UUID, generate a new one but store the original as reference
                    device_uuid = str(uuid.uuid4())
                    logger.info(f"   🔄 Generated UUID {device_uuid} for string phone_number_id {device_id}")
                
                new_device = Device(
                    device_id=device_uuid,
                    busi_user_id=user_id,
                    device_name=f"Official WhatsApp - {official_config.business_number}",
                    device_type=DeviceType.official,  # 🔥 FIXED: Use lowercase 'official' to match enum
                    session_status=SessionStatus.connected if official_config.is_active else SessionStatus.disconnected,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(new_device)
                db.commit()
                
                logger.info(f"   ✅ Created Device for Official WhatsApp: {device_uuid}")
                return {"success": True, "device": new_device, "action": "created_official"}
            
            # Check if device exists in Engine (for unofficial devices)
            engine_devices = self.get_engine_devices()
            engine_device = next((d for d in engine_devices if d["device_id"] == device_id), None)
            
            if not engine_device:
                logger.error(f"   ❌ Device not found in Engine or Official Config: {device_id}")
                return {"success": False, "error": "Device not found in Engine or Official Config"}
            
            # 🔥 AUTO-CREATE DEVICE (PRODUCTION FIX)
            logger.info(f"   🆕 Auto-creating device: {device_id}")
            
            new_device = Device(
                device_id=device_id,
                busi_user_id=user_id,
                device_name=engine_device.get("name", f"Device {device_id[:8]}"),
                device_type=DeviceType.UNOFFICIAL,  # 🔥 FIXED: All engine devices are UNOFFICIAL
                session_status=SessionStatus.connected if engine_device.get("status") == "connected" else SessionStatus.disconnected,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_device)
            db.commit()
            
            logger.info(f"   ✅ Auto-created device: {device_id} → user: {user_id}")
            
            return {"success": True, "device": new_device, "action": "created"}
            
        except Exception as e:
            logger.error(f"❌ Ensure device error: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def sync_all_users_devices(self, db: Session) -> Dict[str, any]:
        """
        Sync devices for all users (admin function)
        """
        logger.info("🔄 SYNCING DEVICES FOR ALL USERS")
        
        try:
            from models import BusiUser  # Fixed: Use BusiUser instead of Business
            
            # Get all users
            users = db.query(BusiUser).all()
            
            total_results = {
                "success": True,
                "users_processed": 0,
                "total_synced": 0,
                "total_created": 0,
                "total_updated": 0,
                "user_results": []
            }
            
            for user in users:
                user_id = str(user.busi_user_id)
                
                logger.info(f"   Processing user: {user_id}")
                user_result = self.sync_user_devices(db, user_id)
                
                total_results["user_results"].append({
                    "user_id": user_id,
                    "result": user_result
                })
                
                if user_result["success"]:
                    total_results["users_processed"] += 1
                    total_results["total_synced"] += user_result.get("synced", 0)
                    total_results["total_created"] += user_result.get("created", 0)
                    total_results["total_updated"] += user_result.get("updated", 0)
                else:
                    total_results["success"] = False
            
            logger.info(f"🏁 ALL USERS SYNC COMPLETE: {total_results}")
            return total_results
            
        except Exception as e:
            logger.error(f"❌ Sync all users error: {e}")
            return {"success": False, "error": str(e)}

# Global instance
device_sync_service = DeviceSyncService()

def sync_user_devices(db: Session, user_id: str) -> Dict[str, any]:
    """Global function for easy access"""
    return device_sync_service.sync_user_devices(db, user_id)

def ensure_device_exists(db: Session, user_id: str, device_id: str) -> Dict[str, any]:
    """Global function for easy access"""
    return device_sync_service.ensure_device_exists(db, user_id, device_id)
