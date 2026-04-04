from sqlalchemy import text
from db.session import engine

def update_schema():
    print("Adding missing columns to 'businesses' table...")
    with engine.connect() as connection:
        try:
            # Add organization_type
            connection.execute(text("ALTER TABLE businesses ADD COLUMN IF NOT EXISTS organization_type VARCHAR(100);"))
            print("Added 'organization_type' column.")
            
            # Add bank_name
            connection.execute(text("ALTER TABLE businesses ADD COLUMN IF NOT EXISTS bank_name VARCHAR(255);"))
            print("Added 'bank_name' column.")
            
            # Add consumption_rate (if missing from previous tasks)
            connection.execute(text("ALTER TABLE businesses ADD COLUMN IF NOT EXISTS consumption_rate FLOAT DEFAULT 0.0;"))
            print("Checked 'consumption_rate' column.")
            
            connection.commit()
            print("Database schema updated successfully!")
            
        except Exception as e:
            print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
