import asyncio
import logging
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

# Import all models
import models
from db.session import SessionLocal
from services.google_sheets_automation_unofficial_only import GoogleSheetsAutomationServiceUnofficial
from models.google_sheet import GoogleSheet

# Setup logging
logging.basicConfig(level=logging.INFO)

async def test_triggers():
    db = SessionLocal()
    try:
        print("Checking GoogleSheet count...")
        count = db.query(GoogleSheet).count()
        print(f"Count: {count}")
        
        service = GoogleSheetsAutomationServiceUnofficial(db)
        print("🚀 STARTING TRIGGER SCAN...")
        await service.process_all_active_triggers()
        print("--- DONE ---")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_triggers())
