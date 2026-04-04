from db.session import SessionLocal
from sqlalchemy import text
import sys

def check_columns():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'sheet_trigger_history'"))
        columns = [row[0] for row in result]
        print(f"Columns in sheet_trigger_history: {columns}")
        
        if 'device_id' not in columns:
            print("CRITICAL MISSING COLUMN: device_id")
        else:
            print("Column device_id exists.")
            
    except Exception as e:
        print(f"Error checking columns: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_columns()
