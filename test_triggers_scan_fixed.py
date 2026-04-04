import asyncio
import logging
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

# Import all models to avoid mapper errors
import models
from db.session import SessionLocal
from services.google_sheets_automation_unofficial_only import GoogleSheetsAutomationServiceUnofficial

# Setup logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

async def test_triggers():
    db = SessionLocal()
    try:
        service = GoogleSheetsAutomationServiceUnofficial(db)
        print("🚀 STARTING TRIGGER SCAN...")
        await service.process_all_active_triggers()
        print("✅ TRIGGER SCAN COMPLETE.")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_triggers())
