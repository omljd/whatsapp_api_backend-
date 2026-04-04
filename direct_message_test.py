#!/usr/bin/env python3
"""
Direct test: Force message sending to your device
"""

import logging
import asyncio
from datetime import datetime
from db.session import SessionLocal
from models.google_sheet import GoogleSheet, GoogleSheetTrigger
from services.google_sheets_automation import GoogleSheetsAutomationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def direct_message_test():
    """Direct test to force message sending"""
    logger.info("🧪 DIRECT TEST: FORCE MESSAGE SENDING")
    logger.info("=" * 70)
    
    db = SessionLocal()
    try:
        # Your device ID
        your_device_id = "36711d22-ac2c-4e85-9b04-3f06a7d73158"
        
        logger.info(f"📱 Your Device ID: {your_device_id}")
        
        # 1. Get any trigger
        trigger = db.query(GoogleSheetTrigger).filter(
            GoogleSheetTrigger.is_enabled == True
        ).first()
        
        if not trigger:
            logger.error("❌ No active trigger found")
            return False
        
        logger.info(f"🧪 Using trigger: {trigger.trigger_id}")
        logger.info(f"   Type: {trigger.trigger_type}")
        logger.info(f"   Device: {trigger.device_id}")
        logger.info(f"   Status column: {trigger.status_column}")
        logger.info(f"   Trigger value: {trigger.trigger_value}")
        logger.info(f"   Message: {trigger.message_template}")
        
        # 2. Get sheet
        sheet = db.query(GoogleSheet).filter(
            GoogleSheet.id == trigger.sheet_id
        ).first()
        
        if not sheet:
            logger.error("❌ Sheet not found")
            return False
        
        logger.info(f"📊 Using sheet: {sheet.sheet_name}")
        
        # 3. Create test row data that WILL match
        test_row_data = {
            'Phone': '9145291501',  # Your phone number
            'Name': 'DIRECT TEST USER',
            'Time': '5.45 PM',
            'Massage': 'DIRECT TEST MESSAGE - PLEASE SEND NOW',
            'Status': 'Send'  # This will match!
        }
        
        row_info = {
            'data': test_row_data,
            'row_number': 999  # Use high number to avoid conflicts
        }
        
        logger.info(f"🧪 Test row data: {test_row_data}")
        
        # 4. Force device ID to yours
        trigger.device_id = your_device_id
        logger.info(f"✅ Forced device_id to: {your_device_id}")
        
        # 5. Process the row
        automation_service = GoogleSheetsAutomationService(db)
        
        logger.info("🧪 PROCESSING TEST ROW...")
        logger.info("🧪 This should send message to your device!")
        
        result = asyncio.run(automation_service.process_row_for_trigger(sheet, trigger, row_info))
        
        logger.info(f"🧪 Processing result: {result}")
        
        # 6. Check trigger history
        logger.info("\n📋 CHECKING TRIGGER HISTORY")
        
        from models.google_sheet import GoogleSheetTriggerHistory
        
        recent_history = db.query(GoogleSheetTriggerHistory).filter(
            GoogleSheetTriggerHistory.phone_number == '+919145291501'  # Your formatted phone
        ).order_by(GoogleSheetTriggerHistory.triggered_at.desc()).limit(5).all()
        
        logger.info(f"📊 Found {len(recent_history)} recent history records for +919145291501")
        
        for record in recent_history:
            logger.info(f"   📅 {record.triggered_at}: {record.status}")
            logger.info(f"      Phone: {record.phone_number}")
            logger.info(f"      Message: {record.message_content[:50]}...")
            if record.error_message:
                logger.info(f"      ❌ Error: {record.error_message}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def show_test_analysis():
    """Show test analysis"""
    logger.info("\n📋 TEST ANALYSIS")
    logger.info("=" * 50)
    
    logger.info("""
🔍 WHAT THIS TEST DOES:
1. Creates a test row with Status = "Send"
2. Forces trigger to use your device ID
3. Processes the row directly
4. Checks if message is sent
5. Reviews trigger history

🔍 EXPECTED BEHAVIOR:
✅ Row matches trigger condition
✅ Phone formatted: 9145291501 → +919145291501
✅ Message sent via your device
✅ Trigger history shows SENT status
✅ You receive WhatsApp message

🔍 POSSIBLE ISSUES:

1️⃣ DEVICE NOT CONNECTED:
   - Device exists in database but not connected to WhatsApp
   - Check device connection in frontend

2️⃣ WHATSAPP ENGINE DOWN:
   - WhatsApp Engine service not running
   - Check if engine is accessible

3️⃣ PHONE NUMBER ISSUE:
   - Phone number format or validation issue
   - Check phone number formatting

4️⃣ MESSAGE TEMPLATE EMPTY:
   - Message template is empty or invalid
   - Check trigger message template

5️⃣ PERMISSIONS ISSUE:
   - No permission to send WhatsApp messages
   - Check WhatsApp permissions

🔧 IF TEST FAILS:

1. CHECK DEVICE CONNECTION:
   - Go to WhatsApp device management
   - Ensure device "vhgfhv" is connected
   - Reconnect if needed

2. CHECK WHATSAPP ENGINE:
   - Check if engine is running on port 3002
   - Restart engine if needed

3. CHECK PHONE NUMBER:
   - Verify 9145291501 is correct
   - Try different phone number

4. CHECK MESSAGE CONTENT:
   - Ensure message template has content
   - Update message template if needed

📱 EXPECTED LOGS:
🎯 Row 999: MATCH! Status 'SEND' == 'SEND'
📱 Raw phone from sheet: 9145291501
📱 Formatted phone: +919145291501
📱 Using unofficial device 36711d22-ac2c-4e85-9b04-3f06a7d73158
📱 Personalized message: DIRECT TEST MESSAGE - PLEASE SEND NOW
📤 Processing row 999 via unofficial device
📱 Sending message via unofficial device to +919145291501
✅ Message sent successfully via unofficial device to +919145291501

🎉 SUCCESS INDICATORS:
✅ Test row processed successfully
✅ Message sent to your device
✅ Trigger history shows SENT
✅ WhatsApp message received

🚀 NEXT STEPS:
1. Run this direct test
2. Check server logs for errors
3. Check WhatsApp for message
4. Review trigger history
5. Fix any issues found

🎯 IF STILL NOT WORKING:
The issue might be with:
- WhatsApp Engine connection
- Device authentication
- Phone number validation
- Message content validation

Check each of these areas systematically.
    """)

if __name__ == "__main__":
    success = direct_message_test()
    show_test_analysis()
    
    if success:
        logger.info("\n🎉 DIRECT TEST COMPLETED!")
        logger.info("📱 Check logs and WhatsApp for message")
    else:
        logger.info("\n❌ DIRECT TEST FAILED")
        logger.info("🔧 Check the errors above")
