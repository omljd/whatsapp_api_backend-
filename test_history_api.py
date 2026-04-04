#!/usr/bin/env python3
"""
Test trigger history API
"""

import logging
from db.session import SessionLocal
from models.google_sheet import GoogleSheetTriggerHistory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_trigger_history():
    """Test trigger history functionality"""
    logger.info("Testing trigger history...")
    
    db = SessionLocal()
    try:
        # Test querying the table
        history = db.query(GoogleSheetTriggerHistory).limit(5).all()
        logger.info(f"Found {len(history)} history records")
        
        # Test API endpoint logic
        from models.google_sheet import GoogleSheet
        
        sheets = db.query(GoogleSheet).all()
        logger.info(f"Found {len(sheets)} sheets")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_trigger_history()
