#!/usr/bin/env python3
"""
Simple test for message sending - bypass time trigger logic
"""

import logging
import asyncio
from datetime import datetime
from db.session import SessionLocal
from models.google_sheet import GoogleSheet, GoogleSheetTrigger
from services.google_sheets_automation import GoogleSheetsAutomationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_simple_message_sending():
    """Test simple message sending without time trigger logic"""
    logger.info("🧪 TESTING SIMPLE MESSAGE SENDING")
    logger.info("=" * 50)
    
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
        
        # Get sheet data
        automation_service = GoogleSheetsAutomationService(db)
        
        try:
            # Get sheet data with headers
            data, headers = automation_service.sheets_service.get_sheet_data_with_headers(
                sheet.spreadsheet_id, "Sheet1"
            )
            logger.info(f"📊 Found {len(data)} rows in sheet")
            logger.info(f"📋 Headers: {headers}")
            
            # Find a row with matching status
            status_column = trigger.status_column or "Status"
            trigger_value = trigger.trigger_value or "Send"
            
            for i, row in enumerate(data):
                # Check if status matches
                row_status = str(row.get(status_column, "")).strip().upper()
                if row_status == trigger_value.upper():
                    logger.info(f"🎯 Found matching row {i+1}: {row}")
                    
                    # Process this row manually
                    row_info = {
                        'data': row,
                        'row_number': i + 1
                    }
                    
                    logger.info("🧪 Processing row manually...")
                    asyncio.run(automation_service.process_row_for_trigger(sheet, trigger, row_info))
                    
                    return True
            
            logger.warning(f"⚠️ No rows found with status '{trigger_value}' in column '{status_column}'")
            logger.info("📋 Sheet data:")
            for i, row in enumerate(data[:5]):
                logger.info(f"   Row {i+1}: {row}")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error getting sheet data: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        return False
    finally:
        db.close()

def show_test_results():
    """Show test results and next steps"""
    logger.info("\n📋 TEST RESULTS")
    logger.info("=" * 50)
    
    logger.info("""
🔍 WHAT THIS TEST DOES:
1. Finds a trigger with device_id
2. Gets the associated Google Sheet
3. Looks for rows with matching status
4. Processes the row manually
5. Attempts to send message via WhatsApp device

🔍 EXPECTED OUTCOMES:

✅ SUCCESS:
- Row found with matching status
- Phone number formatted correctly
- Message sent via WhatsApp device
- Trigger history updated to SENT

❌ FAILURE:
- No matching rows found
- Device not connected
- Phone number invalid
- WhatsApp API error

📱 IF SUCCESS:
- Check WhatsApp for message
- Check trigger history API
- Verify sheet status updated

🔧 IF FAILURE:
1. Check Google Sheet data
2. Verify device connection
3. Check phone number format
4. Review server logs

📋 NEXT STEPS:
1. Add test data to Google Sheet if needed
2. Verify device is connected
3. Check trigger configuration
4. Monitor server logs
5. Test with different triggers
    """)

if __name__ == "__main__":
    success = test_simple_message_sending()
    show_test_results()
    
    if success:
        logger.info("\n🎉 MESSAGE SENDING TEST SUCCESSFUL!")
        logger.info("📱 Check your WhatsApp for the test message")
    else:
        logger.info("\n❌ MESSAGE SENDING TEST FAILED")
        logger.info("🔧 Check the errors and follow the troubleshooting steps")
