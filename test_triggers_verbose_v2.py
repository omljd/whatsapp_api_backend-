import asyncio
import logging
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

# Import all models to ensure mappers are initialized
import models
from db.session import SessionLocal
from services.google_sheets_automation_unofficial_only import GoogleSheetsAutomationServiceUnofficial
from models.google_sheet import GoogleSheet, GoogleSheetTrigger

# Setup logging to console
root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root.addHandler(handler)

async def test_triggers():
    print("--- STARTING VERBOSE TEST ---")
    db = SessionLocal()
    try:
        from sqlalchemy.orm import configure_mappers
        configure_mappers()
        
        # Check database state first
        active_sheets = db.query(GoogleSheet).filter(models.google_sheet.SheetStatus.ACTIVE == models.google_sheet.SheetStatus.ACTIVE).all()
        print(f"Found {len(active_sheets)} total sheets in DB.")
        for s in active_sheets:
            print(f"Sheet: {s.sheet_name} (ID: {s.id}) | Status: {s.status}")
            triggers = db.query(GoogleSheetTrigger).filter(GoogleSheetTrigger.sheet_id == s.id).all()
            print(f"  -> Has {len(triggers)} triggers.")
            for t in triggers:
                print(f"     - Trigger {t.trigger_id}: Type={t.trigger_type}, Enabled={t.is_enabled}, Device={t.device_id}")

        service = GoogleSheetsAutomationServiceUnofficial(db)
        print("\n🚀 EXECUTING process_all_active_triggers()...")
        await service.process_all_active_triggers()
        print("\n--- TEST FINISHED ---")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_triggers())
