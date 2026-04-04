from db.base import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # Check if contact_name and chat_type columns exist
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'whatsapp_inbox' 
            AND column_name IN ('contact_name', 'chat_type')
        """))
        columns = result.fetchall()
        
        print("=== SCHEMA VERIFICATION ===")
        if columns:
            print("✅ New columns found:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        else:
            print("❌ New columns not found")
            
        # Check existing data
        result = conn.execute(text("SELECT COUNT(*) FROM whatsapp_inbox"))
        count = result.fetchone()[0]
        print(f"\n📊 Total messages in inbox: {count}")
        
        # Check if chat_type has values
        result = conn.execute(text("SELECT DISTINCT chat_type FROM whatsapp_inbox"))
        chat_types = [row[0] for row in result.fetchall()]
        print(f"📝 Chat types found: {chat_types}")
        
except Exception as e:
    print(f"❌ Error: {e}")
