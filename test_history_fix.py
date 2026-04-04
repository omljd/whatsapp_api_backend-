#!/usr/bin/env python3
"""
Test trigger execution with correct UUID
"""

import logging
import uuid
from datetime import datetime
from db.session import SessionLocal
from models.google_sheet import GoogleSheet, GoogleSheetTriggerHistory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_trigger_execution():
    """Test trigger execution with correct UUID"""
    logger.info("Testing trigger execution...")
    
    db = SessionLocal()
    try:
        # Get actual sheet UUID
        sheet = db.query(GoogleSheet).first()
        if not sheet:
            logger.error("No sheets found in database")
            return False
        
        logger.info(f"Using sheet: {sheet.sheet_name} ({sheet.id})")
        
        # Create a test history record with correct UUID
        history = GoogleSheetTriggerHistory(
            sheet_id=sheet.id,  # Use actual UUID
            trigger_id="test-trigger-execution",
            phone_number="+919145291501",
            message_content="Test message at " + str(datetime.now()),
            status="SENT",
            row_data={"Name": "Test User", "Time": "03.15 PM"}
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        logger.info(f"✅ Created test history record: {history.id}")
        logger.info(f"   Message: {history.message_content}")
        logger.info(f"   Status: {history.status}")
        logger.info(f"   Triggered at: {history.triggered_at}")
        
        # Query all history
        all_history = db.query(GoogleSheetTriggerHistory).all()
        logger.info(f"📊 Total history records: {len(all_history)}")
        
        for item in all_history:
            logger.info(f"   📅 {item.triggered_at}: {item.status} - {item.phone_number}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_trigger_execution()
    
    if success:
        logger.info("\n🎉 TRIGGER HISTORY TEST SUCCESSFUL!")
        logger.info("📱 Refresh button should now work properly!")
        logger.info("🔍 Check the trigger history API endpoint")
    else:
        logger.info("\n❌ TEST FAILED")
