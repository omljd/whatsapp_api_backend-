#!/usr/bin/env python3
"""
Simple test to check time trigger method
"""

import logging
import asyncio
from datetime import datetime
from db.session import SessionLocal
from models.google_sheet import GoogleSheetTrigger, TriggerType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_simple():
    """Simple test of the time trigger method"""
    db = SessionLocal()
    try:
        # Get a time trigger
        trigger = db.query(GoogleSheetTrigger).filter(
            GoogleSheetTrigger.trigger_type == TriggerType.TIME,
            GoogleSheetTrigger.is_enabled == True
        ).first()
        
        if not trigger:
            logger.info("No time trigger found")
            return
        
        logger.info(f"Found trigger: {trigger.trigger_id}")
        
        # Import and test
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Create service instance
        from services.google_sheets_automation import GoogleSheetsAutomationService
        service = GoogleSheetsAutomationService(db)
        
        # Check if method exists
        if hasattr(service, 'should_run_time_trigger'):
            logger.info("✅ Method should_run_time_trigger exists")
            
            # Test the method
            sheet = db.query(GoogleSheet).filter(
                GoogleSheet.id == trigger.sheet_id
            ).first()
            
            if sheet:
                result = asyncio.run(service.should_run_time_trigger(trigger, sheet, datetime.utcnow()))
                logger.info(f"Method result: {result}")
        else:
            logger.error("❌ Method should_run_time_trigger does not exist")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_simple()
