#!/usr/bin/env python3
"""
Test the specific Google Sheet URL to verify time-based triggers are working
"""

import logging
import asyncio
from datetime import datetime
from db.session import SessionLocal

def get_default_sheet_id():
    """Get default active sheet ID dynamically"""
    from db.session import SessionLocal
    from models.google_sheet import GoogleSheet, SheetStatus
    
    db = SessionLocal()
    try:
        sheet = db.query(GoogleSheet).filter(
            GoogleSheet.status == SheetStatus.ACTIVE
        ).first()
        return sheet.spreadsheet_id if sheet else "1eF28T3dsJ78IaDSVQI0T3wvCD9lQBkqHhzjgYE1mEjw"
    finally:
        db.close()

from models.google_sheet import GoogleSheet, GoogleSheetTrigger, TriggerType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_specific_sheet():
    """Test the specific sheet from the Google Sheets URL"""
    logger.info("🧪 TESTING SPECIFIC GOOGLE SHEET")
    logger.info("=" * 60)
    
    # Extract sheet ID from URL
    sheet_url = "https://docs.google.com/spreadsheets/d/1eF28T3dsJ78IaDSVQI0T3wvCD9lQBkqHhzjgYE1mEjw/edit?gid=0#gid=0"
    sheet_id = get_default_sheet_id()
    
    logger.info(f"📋 Testing sheet ID: {sheet_id}")
    
    db = SessionLocal()
    try:
        # Check if this sheet exists in database
        sheet = db.query(GoogleSheet).filter(
            GoogleSheet.spreadsheet_id == sheet_id
        ).first()
        
        if not sheet:
            logger.error(f"❌ Sheet {sheet_id} not found in database")
            logger.info("💡 Sheet needs to be connected via API first")
            return False
        
        logger.info(f"✅ Found sheet: {sheet.sheet_name}")
        logger.info(f"   Status: {sheet.status}")
        logger.info(f"   User ID: {sheet.user_id}")
        
        # Check triggers for this sheet
        triggers = db.query(GoogleSheetTrigger).filter(
            GoogleSheetTrigger.sheet_id == sheet.id,
            GoogleSheetTrigger.is_enabled == True
        ).all()
        
        logger.info(f"📊 Found {len(triggers)} triggers for this sheet")
        
        time_triggers = [t for t in triggers if t.trigger_type == TriggerType.TIME]
        row_triggers = [t for t in triggers if t.trigger_type != TriggerType.TIME]
        
        logger.info(f"🕐 Time-based triggers: {len(time_triggers)}")
        logger.info(f"📝 Row-based triggers: {len(row_triggers)}")
        
        # Test time trigger logic
        if time_triggers:
            for trigger in time_triggers:
                logger.info(f"\n🔍 Testing time trigger: {trigger.trigger_id}")
                logger.info(f"   Last triggered: {trigger.last_triggered_at}")
                logger.info(f"   Config: {trigger.trigger_config}")
                
                # Import and test the logic
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                from services.google_sheets_automation import GoogleSheetsAutomationService
                
                automation_service = GoogleSheetsAutomationService(db)
                
                # Test the should_run_time_trigger method
                current_time = datetime.utcnow()
                should_run = asyncio.run(automation_service.should_run_time_trigger(trigger, sheet, current_time))
                
                logger.info(f"   Should run now: {should_run}")
                logger.info(f"   Current time: {current_time}")
                
                if should_run:
                    logger.info("🚀 Time trigger should execute NOW!")
                    logger.info("   ✅ This means messages should be sent")
                else:
                    logger.info("⏰ Time trigger not due yet")
                    
                    # Calculate when it will run
                    config = trigger.trigger_config or {}
                    interval = config.get('interval', 3600)
                    last_triggered = trigger.last_triggered_at
                    
                    if last_triggered:
                        from datetime import timedelta
                        next_run = last_triggered + timedelta(seconds=interval)
                        logger.info(f"   Next run: {next_run}")
                        time_until_next = next_run - current_time
                        if time_until_next.total_seconds() > 0:
                            hours = time_until_next.total_seconds() // 3600
                            minutes = (time_until_next.total_seconds() % 3600) // 60
                            logger.info(f"   Time until next run: {hours}h {minutes}m")
        
        # Test manual trigger processing
        logger.info(f"\n🧪 TESTING MANUAL TRIGGER PROCESSING")
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from services.google_sheets_automation import GoogleSheetsAutomationService
        
        automation_service = GoogleSheetsAutomationService(db)
        
        # Test process_sheet_triggers directly
        logger.info("🔄 Calling process_sheet_triggers() directly...")
        result = asyncio.run(automation_service.process_sheet_triggers(sheet))
        logger.info(f"   Result: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing sheet: {e}")
        return False
    finally:
        db.close()

def show_instructions():
    """Show instructions for monitoring"""
    logger.info("\n📋 MONITORING INSTRUCTIONS")
    logger.info("=" * 60)
    
    logger.info("""
🔍 TO MONITOR TIME-BASED TRIGGERS:

1. CHECK SERVER LOGS:
   Look for these log messages:
   - "🕐 Processing time-based trigger {trigger_id}"
   - "🚀 Time trigger {trigger_id} executing NOW"
   - "✅ Time trigger {trigger_id} executed successfully"
   - "📱 Sending messages via Official WhatsApp API"

2. CHECK TRIGGER HISTORY:
   SELECT * FROM sheet_trigger_history WHERE trigger_id = 'your-trigger-id'

3. VERIFY MESSAGE SENDING:
   Check if messages appear in WhatsApp
   Check trigger history records

4. BACKGROUND TASK STATUS:
   Background task should be running and polling every 30 seconds
   Look for: "🔄 LEGACY PROCESSING: Processing triggers"

📋 EXPECTED BEHAVIOR:
- Time triggers should execute every hour (3600 seconds)
- Messages should be sent when trigger executes
- last_triggered_at should be updated
- Process should be visible in logs

🚀 IF TRIGGERS ARE NOT FIRRING:
1. Check if background task is running
2. Check if sheet status is ACTIVE
3. Check if trigger is_enabled = true
4. Check server logs for execution attempts
5. Verify trigger_config has correct interval
    """)

if __name__ == "__main__":
    success = test_specific_sheet()
    show_instructions()
    
    if success:
        logger.info("\n✅ SHEET TEST COMPLETED SUCCESSFULLY")
        logger.info("🚀 Time-based triggers should now work!")
    else:
        logger.info("\n❌ SHEET TEST FAILED")
    
    logger.info("\n🎯 NEXT STEPS:")
    logger.info("1. Monitor server logs for trigger execution")
    logger.info("2. Check if messages are sent to WhatsApp")
    logger.info("3. Verify trigger history records")
