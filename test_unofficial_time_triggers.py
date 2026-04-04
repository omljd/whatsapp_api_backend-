#!/usr/bin/env python3
"""
Test time-based triggers with unofficial devices
"""

import logging
import asyncio
from datetime import datetime
from db.session import SessionLocal
from models.google_sheet import GoogleSheet, GoogleSheetTrigger, TriggerType
from models.device import Device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_unofficial_time_triggers():
    """Test time-based triggers with unofficial devices"""
    logger.info("📱 TESTING TIME-BASED TRIGGERS WITH UNOFFICIAL DEVICES")
    logger.info("=" * 60)
    
    db = SessionLocal()
    try:
        # Check available devices
        devices = db.query(Device).filter(
            Device.session_status == "connected"
        ).all()
        
        logger.info(f"📱 Found {len(devices)} connected devices")
        
        if not devices:
            logger.error("❌ No connected devices found!")
            return False
        
        # Use first connected device
        device = devices[0]
        logger.info(f"✅ Using device: {device.device_name} ({device.device_id})")
        
        # Check existing time triggers
        time_triggers = db.query(GoogleSheetTrigger).filter(
            GoogleSheetTrigger.trigger_type == TriggerType.TIME,
            GoogleSheetTrigger.is_enabled == True
        ).all()
        
        logger.info(f"🕐 Found {len(time_triggers)} time-based triggers")
        
        for trigger in time_triggers:
            logger.info(f"\n🔍 Testing trigger: {trigger.trigger_id}")
            logger.info(f"   Device ID: {trigger.device_id}")
            logger.info(f"   Message Template: {trigger.message_template}")
            logger.info(f"   Config: {trigger.trigger_config}")
            
            # Check if trigger has device_id
            if trigger.device_id:
                logger.info(f"✅ Trigger has device_id: {trigger.device_id}")
                
                # Check if device exists
                trigger_device = db.query(Device).filter(
                    Device.device_id == trigger.device_id,
                    Device.session_status == "connected"
                ).first()
                
                if trigger_device:
                    logger.info(f"✅ Device found and connected: {trigger_device.device_name}")
                else:
                    logger.warning(f"⚠️ Device {trigger.device_id} not found or not connected")
            else:
                logger.warning(f"⚠️ Trigger has no device_id - will use Official API")
        
        # Test time trigger logic
        logger.info(f"\n🧪 TESTING TIME TRIGGER LOGIC")
        from services.google_sheets_automation import GoogleSheetsAutomationService
        
        automation_service = GoogleSheetsAutomationService(db)
        
        for trigger in time_triggers:
            if trigger.device_id:  # Only test unofficial device triggers
                sheet = db.query(GoogleSheet).filter(
                    GoogleSheet.id == trigger.sheet_id
                ).first()
                
                if sheet:
                    current_time = datetime.utcnow()
                    should_run = asyncio.run(automation_service.should_run_time_trigger(trigger, sheet, current_time))
                    
                    logger.info(f"🕐 Trigger {trigger.trigger_id} should run now: {should_run}")
                    logger.info(f"   Current time: {current_time}")
                    
                    if should_run:
                        logger.info(f"🚀 Time trigger should execute NOW!")
                        logger.info(f"   Will send via device: {trigger.device_id}")
                        logger.info(f"   Message: {trigger.message_template}")
                    else:
                        logger.info(f"⏰ Time trigger not due yet")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing unofficial time triggers: {e}")
        return False
    finally:
        db.close()

def show_unofficial_trigger_guide():
    """Show guide for creating unofficial device triggers"""
    logger.info("\n📋 UNOFFICIAL DEVICE TIME TRIGGER GUIDE")
    logger.info("=" * 60)
    
    logger.info("""
🔧 CREATE TIME-BASED TRIGGER WITH UNOFFICIAL DEVICE:

📱 AVAILABLE DEVICES:
- 6 connected devices found
- Use device_id from the list above

📋 TRIGGER CONFIGURATION:

{
  "trigger_type": "time",
  "is_enabled": true,
  "phone_column": "Phone",
  "status_column": "Time",
  "trigger_value": "03.15 PM",
  "message_template": "Hello {{Name}}! This is your scheduled message.",
  "device_id": "ee68cf44-168c-42b0-bf69-bff71cc7110b",  // 🔥 KEY: Use device_id
  "execution_interval": 1800,
  "trigger_config": {
    "specific_times": ["03.15 PM", "03.16 PM", "03.18 PM", "03.20 PM", "03.25 PM", "03.30 PM"],
    "schedule_column": "Time"
  }
}

📱 GOOGLE SHEET STRUCTURE:

┌─────────────────────────────────────────────────────────────┐
│ Phone      │ Name    │ Time     │ Status │ Message        │ Notes │
├─────────────────────────────────────────────────────────────┤
│ +919145291501 │ jaypal │ 03.15 PM │ Send   │ Hello Jaypal! │ Test  │
│ +917507640770 │ vikas  │ 03.16 PM │ Send   │ Hello Vikas!  │ Test  │
│ +919763615655 │ vikas_two │ 03.18 PM │ Send   │ Hello Vikas_Two! │ Test │
│ +917887640770 │ new    │ 03.20 PM │ Send   │ Hello New!    │ Test  │
│ +919145291501 │ jaypal │ 03.25 PM │ Send   │ Hello Japal!  │ Test  │
│ +917507640770 │ vikash │ 03.30 PM │ Send   │ Hello Vikas!  │ Test  │
│ +918767647149 │ om     │ 02.35 PM │ Send   │ Hello Om!     │ Test  │
└─────────────────────────────────────────────────────────────┘

🔄 EXECUTION FLOW:

1. BACKGROUND TASK (Every 30 seconds)
   ↓
2. process_all_active_triggers()
   ↓
3. process_sheet_triggers() - finds device_id
   ↓
4. should_run_time_trigger() - checks timing
   ↓
5. process_single_trigger() - checks device_id
   ↓
6. send_message_via_unofficial_device() - WhatsAppEngineService
   ↓
7. whatsapp_engine_service.send_message(device_id, phone, message)

📱 WHATSAPP ENGINE SERVICE:

- Uses connected WhatsApp devices
- Sends messages via WhatsAppEngineService
- Requires device to be connected
- No Official WhatsApp API needed
- Uses your existing device infrastructure

🔍 MONITORING:

Watch for these logs:
- "🕐 Processing time-based trigger {trigger_id}"
- "🚀 Time trigger {trigger_id} executing NOW"
- "📱 Using unofficial device {device_id} for message sending"
- "📱 Sending message via unofficial device {device_id} to {phone}"
- "✅ Message sent successfully via unofficial device to {phone}"

📋 API CALL TO CREATE TRIGGER:

POST /api/google-sheets/{sheet_id}/triggers
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "trigger_type": "time",
  "is_enabled": true,
  "phone_column": "Phone",
  "status_column": "Time",
  "trigger_value": "03.15 PM",
  "message_template": "Hello {{Name}}! This is your scheduled message.",
  "device_id": "ee68cf44-168c-42b0-bf69-bff71cc7110b",
  "execution_interval": 1800,
  "trigger_config": {
    "specific_times": ["03.15 PM", "03.16 PM", "03.18 PM", "03.20 PM", "03.25 PM", "03.30 PM"],
    "schedule_column": "Time"
  }
}

🚀 EXPECTED BEHAVIOR:

- At 03:15 PM → Sends "Hello jaypal!" to +919145291501 via device
- At 03:16 PM → Sends "Hello vikas!" to +917507640770 via device
- At 03:18 PM → Sends "Hello vikas_two!" to +919763615655 via device
- At 03:20 PM → Sends "Hello new!" to +917887640770 via device
- At 03:25 PM → Sends "Hello jaypal!" to +919145291501 via device
- At 03:30 PM → Sends "Hello vikash!" to +917507640770 via device
- At 02:35 PM → Sends "Hello om!" to +918767647149 via device

✅ REQUIREMENTS:

1. Connected WhatsApp device (6 available)
2. Valid device_id from connected devices
3. WhatsAppEngineService configured
4. Google Sheet with proper structure
5. Time-based trigger with device_id

🎯 NEXT STEPS:

1. Create trigger with device_id using the JSON above
2. Add test data to your Google Sheet
3. Monitor server logs for execution
4. Check WhatsApp for received messages
5. Verify trigger history for execution records
    """)

if __name__ == "__main__":
    success = test_unofficial_time_triggers()
    show_unofficial_trigger_guide()
    
    if success:
        logger.info("\n✅ UNOFFICIAL DEVICE TIME TRIGGER SETUP READY")
        logger.info("📱 Time triggers will use your connected WhatsApp devices!")
    else:
        logger.info("\n❌ SETUP FAILED - CHECK DEVICE CONNECTION")
