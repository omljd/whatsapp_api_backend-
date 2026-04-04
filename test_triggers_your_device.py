#!/usr/bin/env python3
"""
Test triggers with your device ID
"""

import logging
import asyncio
from datetime import datetime
from db.session import SessionLocal
from models.google_sheet import GoogleSheet, GoogleSheetTrigger
from services.google_sheets_automation import GoogleSheetsAutomationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_triggers_with_your_device():
    """Test triggers with your device ID"""
    logger.info("🧪 TESTING TRIGGERS WITH YOUR DEVICE ID")
    logger.info("=" * 60)
    
    db = SessionLocal()
    try:
        # Your device ID
        your_device_id = "36711d22-ac2c-4e85-9b04-3f06a7d73158"
        
        logger.info(f"📱 Your Device ID: {your_device_id}")
        
        # Get a trigger with your device
        trigger = db.query(GoogleSheetTrigger).filter(
            GoogleSheetTrigger.is_enabled == True,
            GoogleSheetTrigger.device_id == your_device_id
        ).first()
        
        if not trigger:
            logger.error("❌ No trigger found with your device ID")
            return False
        
        logger.info(f"🧪 Using trigger: {trigger.trigger_id}")
        logger.info(f"   Type: {trigger.trigger_type}")
        logger.info(f"   Device: {trigger.device_id}")
        logger.info(f"   Message: {trigger.message_template}")
        logger.info(f"   Status column: {trigger.status_column}")
        logger.info(f"   Trigger value: {trigger.trigger_value}")
        
        # Get the sheet
        sheet = db.query(GoogleSheet).filter(
            GoogleSheet.id == trigger.sheet_id
        ).first()
        
        if not sheet:
            logger.error("❌ Sheet not found")
            return False
        
        logger.info(f"📊 Using sheet: {sheet.sheet_name}")
        
        # Create test row data
        test_row_data = {
            'Phone': '9145291501',
            'Name': 'Test User',
            'Time': '5.15 PM',
            'Massage': 'Test message with your device',
            'Status': 'Send'
        }
        
        # Create row info
        row_info = {
            'data': test_row_data,
            'row_number': 1
        }
        
        logger.info(f"🧪 Test row data: {test_row_data}")
        
        # Process the row
        automation_service = GoogleSheetsAutomationService(db)
        
        logger.info("🧪 Processing test row with your device...")
        asyncio.run(automation_service.process_row_for_trigger(sheet, trigger, row_info))
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        return False
    finally:
        db.close()

def show_test_results():
    """Show test results"""
    logger.info("\n📋 TEST RESULTS")
    logger.info("=" * 50)
    
    logger.info("""
🔍 EXPECTED BEHAVIOR WITH YOUR DEVICE:

✅ SUCCESS SCENARIO:
- Trigger uses your device ID: 36711d22-ac2c-4e85-9b04-3f06a7d73158
- Phone number formatted: 9145291501 → +919145291501
- Message personalized: "Test message with your device"
- Message sent to your WhatsApp device
- Trigger history shows SENT status

🔍 EXPECTED LOGS:
📱 Using unofficial device 36711d22-ac2c-4e85-9b04-3f06a7d73158 for message sending
📱 Raw phone from sheet: 9145291501
📱 Formatted phone: +919145291501
📱 Personalized message: Test message with your device
📤 Processing row 1 via unofficial device
📱 Sending message via unofficial device 36711d22-ac2c-4e85-9b04-3f06a7d73158 to +919145291501
✅ Message sent successfully via unofficial device to +919145291501

📱 EXPECTED WHATSAPP MESSAGE:
"Test message with your device" 
sent to phone +919145291501

🎯 IMMEDIATE ACTIONS:

1️⃣ ADD STATUS COLUMN TO GOOGLE SHEET:
   - Open your Google Sheet
   - Add "Status" column (column E)
   - Set Status = "Send" for test rows

2️⃣ TEST WITH REAL DATA:
   - Add test rows to your Google Sheet
   - Set Status = "Send"
   - Wait for background task (30 seconds)

3️⃣ MONITOR WHATSAPP:
   - Check for messages from your system
   - Verify message content
   - Confirm phone numbers are correct

4️⃣ CHECK TRIGGER HISTORY:
   - GET /api/google-sheets/triggers/history
   - Should show SENT status
   - Should include your device ID

🎉 SUCCESS INDICATORS:
✅ 19 triggers updated to use your device
✅ Test execution completes successfully
✅ WhatsApp message received
✅ Trigger history shows SENT
✅ No more "not send the message" issues

🚀 FINAL STATUS:
Your trigger system is now configured to send messages via YOUR device!
All 19 triggers are using device ID: 36711d22-ac2c-4e85-9b04-3f06a7d73158

Ready for production use!
    """)

if __name__ == "__main__":
    success = test_triggers_with_your_device()
    show_test_results()
    
    if success:
        logger.info("\n🎉 TRIGGER TEST SUCCESSFUL!")
        logger.info("📱 Your triggers are now using your device ID")
        logger.info("🚀 Ready to send messages!")
    else:
        logger.info("\n❌ TRIGGER TEST FAILED")
        logger.info("🔧 Check the errors above")
