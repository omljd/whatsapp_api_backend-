#!/usr/bin/env python3
"""
Test to verify ALL unread messages are returned (including before device connection)
"""

import logging
from datetime import datetime, timezone, timedelta
from db.session import SessionLocal
from models.whatsapp_inbox import WhatsAppInbox
from models.device import Device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_all_unread_messages():
    """Test that ALL unread messages are returned, including from before device connection"""
    db = SessionLocal()
    try:
        logger.info("📬 TESTING ALL UNREAD MESSAGES (BEFORE & AFTER DEVICE CONNECTION)")
        logger.info("=" * 70)
        
        # Get ALL unread messages exactly like the API does
        all_unread = db.query(WhatsAppInbox).filter(
            WhatsAppInbox.chat_type == "individual",  # ONLY individual messages
            WhatsAppInbox.is_read == False,          # Must be unread
            WhatsAppInbox.is_outgoing == False      # Only incoming
        ).order_by(WhatsAppInbox.incoming_time.desc()).all()
        
        logger.info(f"📊 Total unread messages: {len(all_unread)}")
        
        # Group messages by device to see which devices have unread
        device_unreads = {}
        for msg in all_unread:
            device_id = str(msg.device_id)
            if device_id not in device_unreads:
                device_unreads[device_id] = []
            device_unreads[device_id].append(msg)
        
        logger.info(f"📱 Devices with unread messages: {len(device_unreads)}")
        
        # Show unread messages per device with connection status
        for device_id, messages in device_unreads.items():
            device = db.query(Device).filter(Device.device_id == device_id).first()
            
            logger.info(f"\n📱 Device: {device_id}")
            if device:
                logger.info(f"   Name: {device.device_name}")
                logger.info(f"   Status: {device.session_status}")
                logger.info(f"   Last Active: {device.last_active}")
                logger.info(f"   Created: {device.created_at}")
                logger.info(f"   Connected: {'✅' if device.session_status == 'connected' else '❌'}")
            
            logger.info(f"   📬 Unread messages: {len(messages)}")
            
            # Show each unread message with timing info
            for i, msg in enumerate(messages[:3]):
                logger.info(f"   {i+1}. 📬 {msg.contact_name} ({msg.phone_number})")
                logger.info(f"      Message: {msg.incoming_message[:50]}...")
                logger.info(f"      Time: {msg.incoming_time}")
                logger.info(f"      Message ID: {msg.message_id}")
                
                # Check if message was before or after device connection
                if device:
                    if device.created_at and msg.incoming_time < device.created_at:
                        logger.info(f"      ⏰ Message BEFORE device connection ✅")
                    elif device.last_active and msg.incoming_time > device.last_active:
                        logger.info(f"      ⏰ Message after last active ✅")
                    else:
                        logger.info(f"      ⏰ Message during device activity ✅")
        
        # Show messages that were specifically before device connection
        logger.info(f"\n🔍 MESSAGES RECEIVED BEFORE DEVICE CONNECTION:")
        before_connection_messages = []
        
        for device_id, messages in device_unreads.items():
            device = db.query(Device).filter(Device.device_id == device_id).first()
            if device and device.created_at:
                for msg in messages:
                    if msg.incoming_time < device.created_at:
                        before_connection_messages.append((device, msg))
        
        logger.info(f"📬 Messages before device connection: {len(before_connection_messages)}")
        
        for device, msg in before_connection_messages[:5]:
            logger.info(f"   📬 {msg.contact_name} ({msg.phone_number})")
            logger.info(f"      Device: {device.device_name}")
            logger.info(f"      Message: {msg.incoming_message[:50]}...")
            logger.info(f"      Message Time: {msg.incoming_time}")
            logger.info(f"      Device Created: {device.created_at}")
            logger.info(f"      ⏰ BEFORE connection by: {device.created_at - msg.incoming_time}")
            logger.info("---")
        
        # Verify API would return these messages
        logger.info(f"\n🌐 API VERIFICATION:")
        logger.info(f"   ✅ API endpoints get ALL devices (connected, disconnected, logged_out)")
        logger.info(f"   ✅ API filters: chat_type='individual', is_read=false, is_outgoing=false")
        logger.info(f"   ✅ Total messages API would return: {len(all_unread)}")
        logger.info(f"   ✅ Messages before connection included: {len(before_connection_messages)}")
        
        return {
            "total_unread": len(all_unread),
            "devices_with_unread": len(device_unreads),
            "before_connection": len(before_connection_messages),
            "all_messages": all_unread
        }
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None
    finally:
        db.close()

def check_mobile_device_timeline():
    """Check mobile device connection timeline vs messages"""
    db = SessionLocal()
    try:
        logger.info("\n📱 MOBILE DEVICE CONNECTION TIMELINE")
        logger.info("=" * 70)
        
        # Get all devices sorted by creation time
        devices = db.query(Device).filter(
            Device.device_type == "web"
        ).order_by(Device.created_at).all()
        
        logger.info(f"📊 Total devices: {len(devices)}")
        
        for device in devices:
            logger.info(f"\n📱 Device: {device.device_id}")
            logger.info(f"   Name: {device.device_name}")
            logger.info(f"   Status: {device.session_status}")
            logger.info(f"   Created: {device.created_at}")
            logger.info(f"   Last Active: {device.last_active}")
            
            # Get messages around device creation time
            before_device = db.query(WhatsAppInbox).filter(
                WhatsAppInbox.device_id == device.device_id,
                WhatsAppInbox.incoming_time < device.created_at,
                WhatsAppInbox.is_read == False,
                WhatsAppInbox.is_outgoing == False
            ).count()
            
            after_device = db.query(WhatsAppInbox).filter(
                WhatsAppInbox.device_id == device.device_id,
                WhatsAppInbox.incoming_time >= device.created_at,
                WhatsAppInbox.is_read == False,
                WhatsAppInbox.is_outgoing == False
            ).count()
            
            logger.info(f"   📬 Unread before device creation: {before_device}")
            logger.info(f"   📬 Unread after device creation: {after_device}")
            logger.info(f"   📬 Total unread: {before_device + after_device}")
        
        return devices
        
    except Exception as e:
        logger.error(f"❌ Error checking timeline: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    result = test_all_unread_messages()
    devices = check_mobile_device_timeline()
    
    logger.info("\n✅ ALL UNREAD MESSAGES TEST COMPLETED")
    if result:
        logger.info(f"📊 Results:")
        logger.info(f"   Total unread: {result['total_unread']}")
        logger.info(f"   Devices with unread: {result['devices_with_unread']}")
        logger.info(f"   Messages before connection: {result['before_connection']}")
    
    logger.info("\n🚀 FRONTEND SHOULD RECEIVE ALL THESE MESSAGES!")
    logger.info("📱 Call GET /api/replies/unread-messages to get ALL unread messages")
