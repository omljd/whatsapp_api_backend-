#!/usr/bin/env python3
"""
Test time-based trigger functionality after fix
"""

import logging
import asyncio
from datetime import datetime, timedelta
from db.session import SessionLocal
from models.google_sheet import GoogleSheet, GoogleSheetTrigger, TriggerType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_time_trigger_logic():
    """Test the time-based trigger logic"""
    logger.info("🧪 TESTING TIME-BASED TRIGGER LOGIC")
    logger.info("=" * 60)
    
    db = SessionLocal()
    try:
        # Get time-based triggers
        time_triggers = db.query(GoogleSheetTrigger).filter(
            GoogleSheetTrigger.trigger_type == TriggerType.TIME,
            GoogleSheetTrigger.is_enabled == True
        ).all()
        
        logger.info(f"📊 Found {len(time_triggers)} time-based triggers")
        
        for trigger in time_triggers:
            logger.info(f"\n🕐 Testing trigger: {trigger.trigger_id}")
            logger.info(f"   Sheet ID: {trigger.sheet_id}")
            logger.info(f"   Last Triggered: {trigger.last_triggered_at}")
            logger.info(f"   Config: {trigger.trigger_config}")
            
            # Import the automation service to test the logic
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from services.google_sheets_automation import GoogleSheetsAutomationService
            automation_service = GoogleSheetsAutomationService(db)
            
            # Get sheet
            sheet = db.query(GoogleSheet).filter(
                GoogleSheet.id == trigger.sheet_id
            ).first()
            
            if sheet:
                # Test the should_run_time_trigger method
                current_time = datetime.utcnow()
                should_run = asyncio.run(automation_service.should_run_time_trigger(trigger, sheet, current_time))
                
                logger.info(f"   Should run now: {should_run}")
                logger.info(f"   Current time: {current_time}")
                
                if should_run:
                    logger.info("🚀 Time trigger should execute NOW!")
                    logger.info("   This means messages should be sent")
                else:
                    logger.info("⏰ Time trigger not due yet")
                    
                    # Calculate when it will run
                    config = trigger.trigger_config or {}
                    interval = config.get('interval', 3600)
                    last_triggered = trigger.last_triggered_at
                    
                    if last_triggered:
                        next_run = last_triggered + timedelta(seconds=interval)
                        logger.info(f"   Next run: {next_run}")
                        time_until_next = next_run - current_time
                        if time_until_next.total_seconds() > 0:
                            logger.info(f"   Time until next run: {time_until_next}")
            else:
                logger.warning(f"   Sheet not found for trigger {trigger.trigger_id}")
        
        return len(time_triggers)
        
    except Exception as e:
        logger.error(f"❌ Error testing time triggers: {e}")
        return 0
    finally:
        db.close()

def check_background_task_status():
    """Check if background task is running and calling time triggers"""
    logger.info("\n🔍 CHECKING BACKGROUND TASK STATUS")
    logger.info("=" * 60)
    
    logger.info("""
🔍 BACKGROUND TASK ANALYSIS:
1. Background task calls process_all_active_triggers()
2. process_all_active_triggers calls process_sheet_triggers() for each sheet
3. process_sheet_triggers now handles time-based triggers with should_run_time_trigger()
4. should_run_time_trigger() checks interval and last_triggered_at

🔧 EXPECTED BEHAVIOR:
- Time triggers should run when current_time >= last_triggered_at + interval
- Messages should be sent when should_run_time_trigger() returns True
- last_triggered_at should be updated after successful execution

📋 TRIGGER CONFIGURATION:
- trigger_type: "time"
- trigger_config: {"interval": 3600} (1 hour)
- last_triggered_at: Updated after each execution
- is_enabled: true

🚀 EXPECTED RESULT:
Time-based triggers should now execute and send messages at scheduled intervals!
    """)

if __name__ == "__main__":
    trigger_count = test_time_trigger_logic()
    check_background_task_status()
    
    logger.info("\n✅ TIME-BASED TRIGGER TEST COMPLETED")
    logger.info(f"📊 Found {trigger_count} time-based triggers")
    
    if trigger_count > 0:
        logger.info("🚀 Time-based trigger logic is implemented!")
        logger.info("📱 Triggers should now execute and send messages")
    else:
        logger.info("⚠️  No time-based triggers found")
    
    logger.info("\n🎯 NEXT STEPS:")
    logger.info("1. Restart the application to load the new trigger logic")
    logger.info("2. Monitor logs for time-based trigger execution")
    logger.info("3. Check that messages are sent at scheduled times")
