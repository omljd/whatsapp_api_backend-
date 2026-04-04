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

# Setup logging to console
root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root.addHandler(handler)

async def test_triggers():
    print("--- STARTING TEST ---")
    db = SessionLocal()
    try:
        from sqlalchemy.orm import configure_mappers
        print("Configuring mappers...")
        configure_mappers()
        print("Mappers configured successfully")
        
        service = GoogleSheetsAutomationServiceUnofficial(db)
        print("🚀 STARTING TRIGGER SCAN...")
        await service.process_all_active_triggers()
        print("--- ENDING TEST ---")
    except Exception as e:
        print(f"❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_triggers())
