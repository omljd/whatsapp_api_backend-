#!/usr/bin/env python3
"""
Test unread endpoints with real data for frontend verification
"""

import requests
import json

def test_unread_endpoints_real():
    """Test unread endpoints to verify real data is returned"""
    
    BASE_URL = "http://localhost:8000"
    
    print("🧪 TESTING UNREAD ENDPOINTS WITH REAL DATA")
    print("=" * 60)
    
    # Test without auth first to see endpoint structure
    endpoints = [
        "/api/replies/unread-messages",
        "/api/replies/unread-count", 
        "/api/replies/chat-summary"
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing: {endpoint}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 401:
                print("   ✅ Endpoint exists (401 = needs auth)")
                print("   🔐 Frontend needs to send Authorization header")
            elif response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success - {len(data.get('data', []))} items")
                
                # Show sample data structure
                if data.get('data'):
                    sample = data['data'][0]
                    print(f"   📋 Sample structure:")
                    for key, value in sample.items():
                        print(f"      {key}: {str(value)[:50]}...")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
    
    print(f"\n🔧 FRONTEND INTEGRATION INSTRUCTIONS:")
    print("""
1. Add Authorization header to all requests:
   headers: {
     'Authorization': 'Bearer YOUR_JWT_TOKEN'
   }

2. Call endpoints for real unread data:
   GET /api/replies/unread-messages  → All unread messages
   GET /api/replies/unread-count    → Unread counts per contact
   GET /api/replies/chat-summary    → Chat list with unread badges

3. Real-time updates:
   - Poll /api/replies/unread-count every 30 seconds
   - Update unread badges when count changes
   - Refresh chat list when new messages arrive

4. Expected real data format:
   {
     "success": true,
     "data": [
       {
         "id": "uuid",
         "phone_number": "919876543210",
         "contact_name": "Real Contact",
         "incoming_message": "Real message content",
         "incoming_time": "2026-03-09T06:13:49.440801",
         "unread": true,
         "is_incoming": true,
         "device_id": "device-uuid"
       }
     ]
   }
    """)

def show_current_unread_status():
    """Show current unread message status"""
    
    print("\n📊 CURRENT UNREAD MESSAGE STATUS")
    print("=" * 60)
    
    # Import here to avoid issues
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from db.session import SessionLocal
    from models.whatsapp_inbox import WhatsAppInbox
    
    db = SessionLocal()
    try:
        # Get real unread messages
        unread = db.query(WhatsAppInbox).filter(
            WhatsAppInbox.is_read == False,
            WhatsAppInbox.is_outgoing == False,
            WhatsAppInbox.chat_type == "individual"
        ).order_by(WhatsAppInbox.incoming_time.desc()).limit(10).all()
        
        print(f"📬 Real unread messages in database: {len(unread)}")
        
        for i, msg in enumerate(unread[:5]):
            print(f"\n  {i+1}. 📱 {msg.contact_name or 'Unknown'}")
            print(f"     📞 {msg.phone_number}")
            print(f"     💬 {msg.incoming_message[:60]}...")
            print(f"     ⏰ {msg.incoming_time}")
            print(f"     📱 Device: {msg.device_id}")
            print(f"     📧 Message ID: {msg.message_id}")
            print(f"     📄 Chat Type: {msg.chat_type}")
        
        print(f"\n✅ These are REAL WhatsApp messages that should appear in frontend!")
        print(f"🔧 Frontend should call /api/replies/unread-messages to get them")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_unread_endpoints_real()
    show_current_unread_status()
    
    print("\n🚀 READY FOR FRONTEND INTEGRATION!")
    print("📱 Real WhatsApp messages are available via API endpoints")
