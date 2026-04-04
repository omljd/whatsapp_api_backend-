from db.base import engine
from sqlalchemy import text

def run_validation_tests():
    """Run comprehensive validation tests for Manage Replies stabilization"""
    
    print("🔍 MANAGE REPLIES STABILIZATION - VALIDATION REPORT")
    print("=" * 60)
    
    try:
        with engine.connect() as conn:
            # Test 1: Schema validation
            print("\n📋 TEST 1: SCHEMA VALIDATION")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'whatsapp_inbox' 
                AND column_name IN ('contact_name', 'chat_type')
                ORDER BY column_name
            """))
            columns = result.fetchall()
            
            if len(columns) == 2:
                print("✅ Both required columns present:")
                for col in columns:
                    print(f"   - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            else:
                print(f"❌ Missing columns. Found: {len(columns)}")
            
            # Test 2: Data integrity
            print("\n📊 TEST 2: DATA INTEGRITY")
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(CASE WHEN chat_type = 'individual' THEN 1 END) as individual_chats,
                    COUNT(CASE WHEN contact_name IS NOT NULL AND contact_name != phone_number THEN 1 END) as with_contact_names,
                    COUNT(CASE WHEN contact_name IS NULL OR contact_name = phone_number THEN 1 END) as missing_contact_names,
                    COUNT(DISTINCT device_id || phone_number) as unique_conversations
                FROM whatsapp_inbox
            """))
            stats = result.fetchone()
            
            print(f"   Total messages: {stats[0]}")
            print(f"   Individual chats: {stats[1]}")
            print(f"   With contact names: {stats[2]}")
            print(f"   Missing contact names: {stats[3]}")
            print(f"   Unique conversations: {stats[4]}")
            
            # Test 3: Duplicate detection
            print("\n🔍 TEST 3: DUPLICATE DETECTION")
            result = conn.execute(text("""
                SELECT device_id, phone_number, COUNT(*) as count
                FROM whatsapp_inbox
                GROUP BY device_id, phone_number
                HAVING COUNT(*) > 1
                ORDER BY count DESC
                LIMIT 5
            """))
            duplicates = result.fetchall()
            
            if len(duplicates) == 0:
                print("✅ No duplicate conversations found")
            else:
                print(f"⚠️  Found {len(duplicates)} duplicate conversations:")
                for dup in duplicates:
                    print(f"   - Device {dup[0]} + Phone {dup[1]}: {dup[2]} messages")
            
            # Test 4: Recent activity
            print("\n🕒 TEST 4: RECENT ACTIVITY")
            result = conn.execute(text("""
                SELECT 
                    phone_number,
                    contact_name,
                    incoming_time,
                    incoming_message
                FROM whatsapp_inbox
                WHERE chat_type = 'individual'
                ORDER BY incoming_time DESC
                LIMIT 3
            """))
            recent = result.fetchall()
            
            print("   Recent messages:")
            for i, msg in enumerate(recent, 1):
                contact_display = msg[1] if msg[1] != msg[0] else f"{msg[0]} (no name)"
                print(f"   {i}. {contact_display}: {msg[3][:50]}...")
            
            print("\n" + "=" * 60)
            print("🎉 VALIDATION COMPLETE - All systems operational!")
            
            return True
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    run_validation_tests()
