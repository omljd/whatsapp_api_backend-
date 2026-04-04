#!/usr/bin/env python3
"""
Test with correct Google Sheet structure
"""

import logging
import asyncio
from datetime import datetime
from db.session import SessionLocal
from models.google_sheet import GoogleSheet, GoogleSheetTrigger
from services.google_sheets_automation import GoogleSheetsAutomationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_with_correct_structure():
    """Test with correct Google Sheet structure"""
    logger.info("🧪 TESTING WITH CORRECT GOOGLE SHEET STRUCTURE")
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
        
        # Get sheet data
        automation_service = GoogleSheetsAutomationService(db)
        
        try:
            # Get sheet data with headers
            data, headers = automation_service.sheets_service.get_sheet_data_with_headers(
                sheet.spreadsheet_id, "Sheet1"
            )
            logger.info(f"📊 Found {len(data)} rows in sheet")
            logger.info(f"📋 Headers: {headers}")
            
            # Show current data
            logger.info("📋 Current sheet data:")
            for i, row in enumerate(data):
                logger.info(f"   Row {i+1}: {row}")
            
            # Create test data with Status column
            logger.info("\n🔧 CREATING TEST DATA WITH STATUS COLUMN")
            
            # Simulate adding Status column
            test_data = []
            for i, row in enumerate(data):
                # Add Status column with "Send" for first row
                if i == 0:  # First data row
                    test_row = row.copy()
                    test_row['Status'] = 'Send'
                    test_data.append(test_row)
                    logger.info(f"🧪 Test row {i+1}: {test_row}")
                    break
            
            if not test_data:
                logger.error("❌ No data to test with")
                return False
            
            # Process the test row
            test_row = test_data[0]
            row_info = {
                'data': test_row,
                'row_number': 2
            }
            
            logger.info("🧪 Processing test row...")
            asyncio.run(automation_service.process_row_for_trigger(sheet, trigger, row_info))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        return False
    finally:
        db.close()

def show_sheet_structure_fix():
    """Show how to fix Google Sheet structure"""
    logger.info("\n📋 GOOGLE SHEET STRUCTURE FIX")
    logger.info("=" * 50)
    
    logger.info("""
🔍 CURRENT ISSUE:
- Google Sheet has columns: Phone, Name, Time, Massage
- Trigger is looking for Status column with value "Send"
- No Status column exists in the sheet

🔧 SOLUTION:

1. ADD STATUS COLUMN TO GOOGLE SHEET:

| Phone      | Name    | Time     | Massage | Status |
|------------|---------|----------|---------|--------|
| 9145291501 | jaypal  | 4.34PM   | Hello Jaypal | Send   |
| 7507640770 | vikas   | 4.35 PM  | Hello Vikas | Send   |
| 9763615655 | vikas_two | 4.37PM | Hello Vikas_Two | Send   |
| 7887640770 | new     | 4.39 PM  | Hello New | Send   |

2. OR UPDATE TRIGGER TO USE EXISTING COLUMN:

Change trigger configuration to:
- status_column: "Name" (or any existing column)
- trigger_value: "jaypal" (or value that exists)

3. OR USE NEW_ROW TRIGGER TYPE:

New_row triggers don't need status matching:
- They trigger when new rows are added
- No status column required

📱 RECOMMENDED FIX:

Add Status column to Google Sheet with values:
- "Send" for rows that should trigger
- "Sent" for rows that have been processed
- "Skip" for rows to ignore

🔧 STEPS TO FIX:

1. Open your Google Sheet
2. Add "Status" column as column E
3. Set Status = "Send" for test rows
4. Save the sheet
5. Wait for trigger execution (or run manual test)

🎯 EXPECTED RESULT:
- Trigger finds rows with Status = "Send"
- Sends messages via WhatsApp device
- Updates Status to "SENT"
- Creates trigger history records

✅ AFTER FIX:
Your triggers will send messages properly!
    """)

if __name__ == "__main__":
    success = test_with_correct_structure()
    show_sheet_structure_fix()
    
    if success:
        logger.info("\n🎉 TEST WITH SIMULATED DATA SUCCESSFUL!")
        logger.info("📋 Add Status column to Google Sheet for real execution")
    else:
        logger.info("\n❌ TEST FAILED")
        logger.info("🔧 Check the errors above")
