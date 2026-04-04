#!/usr/bin/env python3
"""
Test message sending with bypassed logic
"""

import logging
import asyncio
from datetime import datetime
from db.session import SessionLocal
from models.google_sheet import GoogleSheet, GoogleSheetTrigger
from services.google_sheets_automation import GoogleSheetsAutomationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bypassed_message_sending():
    """Test message sending with bypassed logic"""
    logger.info("🧪 TESTING BYPASSED MESSAGE SENDING")
    logger.info("=" * 60)
    
    db = SessionLocal()
    try:
        # Get a trigger with device_id
        trigger = db.query(GoogleSheetTrigger).filter(
            GoogleSheetTrigger.is_enabled == True,
            GoogleSheetTrigger.device_id.isnot(None)
        ).first()
        
        if not trigger:
            logger.error("❌ No trigger with device_id found")
            return False
        
        logger.info(f"🧪 Using trigger: {trigger.trigger_id}")
        logger.info(f"   Type: {trigger.trigger_type}")
        logger.info(f"   Device: {trigger.device_id}")
        logger.info(f"   Message: {trigger.message_template}")
        
        # Get the sheet
        sheet = db.query(GoogleSheet).filter(
            GoogleSheet.id == trigger.sheet_id
        ).first()
        
        if not sheet:
            logger.error("❌ Sheet not found")
            return False
        
        logger.info(f"📊 Using sheet: {sheet.sheet_name}")
        
        # Create test row data manually
        test_row_data = {
            'Phone': '9145291501',
            'Name': 'Test User',
            'Time': '4.50 PM',
            'Massage': 'Test message',
            'Status': 'Send'
        }
        
        # Create row info
        row_info = {
            'data': test_row_data,
            'row_number': 1
        }
        
        logger.info(f"🧪 Test row data: {test_row_data}")
        
        # Process the row directly
        automation_service = GoogleSheetsAutomationService(db)
        
        logger.info("🧪 Processing test row directly...")
        asyncio.run(automation_service.process_row_for_trigger(sheet, trigger, row_info))
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        return False
    finally:
        db.close()

def show_bypass_test_results():
    """Show bypass test results"""
    logger.info("\n📋 BYPASS TEST RESULTS")
    logger.info("=" * 50)
    
    logger.info("""
🧪 WHAT THIS TEST DOES:
1. Creates a test row with all required data
2. Bypasses Google Sheet reading
3. Calls process_row_for_trigger directly
4. Tests the complete message sending flow

🔍 EXPECTED OUTCOMES:

✅ SUCCESS:
- Phone number formatted: 9145291501 → +919145291501
- Message template personalized: "Hello Test User! Test message"
- Device found and connected
- WhatsApp message sent successfully
- Trigger history created with SENT status

❌ FAILURE:
- Device not found or not connected
- Phone number formatting error
- WhatsApp engine error
- Template missing or invalid

🔍 EXPECTED LOGS:
📱 Raw phone from sheet: 9145291501
📱 Formatted phone: +919145291501
📱 Using unofficial device ee68cf44-168c-42b0-bf69-bff71cc7110b
📱 Personalized message: Hello Test User! Test message
📤 Processing row 1 via unofficial device
📱 Sending message via unofficial device ee68cf44-168c-42b0-bf69-bff71cc7110b to +919145291501
✅ Message sent successfully via unofficial device to +919145291501

📱 IF SUCCESS:
- Check WhatsApp for message: "Hello Test User! Test message"
- Check trigger history for SENT record
- Check Google Sheet for status update

🔧 IF STILL FAILING:
1. Check device connection in frontend
2. Verify WhatsAppEngineService is working
3. Check phone number formatting
4. Check message template content
5. Review server logs for specific errors

✅ THIS TEST WILL CONFIRM:
- Phone number formatting works
- WhatsAppEngineService.send_message() works
- Device connection works
- Message sending works end-to-end
    """)

if __name__ == "__main__":
    success = test_bypassed_message_sending()
    show_bypass_test_results()
    
    if success:
        logger.info("\n🎉 BYPASS TEST COMPLETE!")
        logger.info("📱 Check WhatsApp for test message")
        logger.info("📋 Check trigger history for SENT record")
    else:
        logger.info("\n❌ BYPASS TEST FAILED")
        logger.info("🔧 Check the errors above")
