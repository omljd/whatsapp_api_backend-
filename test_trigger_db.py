import json
import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.session import SessionLocal
from models.google_sheet import GoogleSheetTrigger
from datetime import datetime, timezone

def check_triggers():
    session = SessionLocal()
    try:
        triggers = session.query(GoogleSheetTrigger).all()
        print(f"Total triggers: {len(triggers)}")
        for t in triggers:
            print(f"- Trigger ID: {t.trigger_id}")
            print(f"  Type: {t.trigger_type}")
            print(f"  Phone Column: {t.phone_column}")
            print(f"  Send Time Col: {t.send_time_column}")
            print(f"  Status Col: {t.status_column}")
            print(f"  Enabled: {t.is_enabled}")
            print(f"  Last Triggered: {t.last_triggered_at}")
    finally:
        session.close()

if __name__ == "__main__":
    check_triggers()
