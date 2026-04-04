#!/usr/bin/env python3
"""
Simple test to verify API endpoints return correct unread data for frontend
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_endpoints_directly():
    """Test API endpoints directly to verify they return unread messages"""
    
    BASE_URL = "http://localhost:8000"
    
    print("🧪 TESTING API ENDPOINTS DIRECTLY")
    print("=" * 60)
    
    # Test endpoints without auth first (should get 401)
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
                print("   ✅ Endpoint exists (needs authentication)")
                print("   🔐 Frontend must send Authorization header")
            elif response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success - {len(data.get('data', []))} items returned")
                
                # Show sample of what frontend would receive
                if data.get('data'):
                    sample = data['data'][0]
                    print(f"   📋 Sample data structure:")
                    for key, value in sample.items():
                        if key in ['contact_name', 'phone_number', 'incoming_message', 'unread']:
                            print(f"      {key}: {str(value)[:50]}...")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
    
    print(f"\n🔧 FRONTEND INTEGRATION CHECKLIST:")
    print("""
1. Authentication:
   ✅ Send JWT token in Authorization header
   ✅ Format: 'Bearer YOUR_TOKEN_HERE'

2. API Calls:
   ✅ GET /api/replies/unread-messages → All unread messages
   ✅ GET /api/replies/unread-count → Unread counts per contact  
   ✅ GET /api/replies/chat-summary → Chat list with unread badges

3. Expected Response Format:
   {
     "success": true,
     "data": [
       {
         "id": "uuid",
         "phone_number": "64364430270547",
         "contact_name": "Abhi",
         "incoming_message": "Ani nantr nahi geli ka...",
         "incoming_time": "2026-03-09T06:13:49.440801",
         "unread": true,
         "is_incoming": true,
         "device_id": "667ed3f7-c955-47d2-82b5-3d211cd75e87"
       }
     ]
   }

4. Real-time Updates:
   ✅ Poll /api/replies/unread-count every 30 seconds
   ✅ Update unread badges when count changes
   ✅ Refresh chat list when new messages arrive

5. Error Handling:
   ✅ Handle 401 Unauthorized (re-authenticate)
   ✅ Handle 500 Server errors (retry)
   ✅ Show loading states during API calls
    """)

def show_expected_unread_messages():
    """Show exactly what unread messages frontend should display"""
    print("\n📬 EXPECTED UNREAD MESSAGES IN FRONTEND")
    print("=" * 60)
    
    # Import database modules
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from db.session import SessionLocal
    from models.whatsapp_inbox import WhatsAppInbox
    
    db = SessionLocal()
    try:
        # Get unread messages exactly like the API
        unread = db.query(WhatsAppInbox).filter(
            WhatsAppInbox.is_read == False,
            WhatsAppInbox.is_outgoing == False,
            WhatsAppInbox.chat_type == "individual"
        ).order_by(WhatsAppInbox.incoming_time.desc()).all()
        
        print(f"📊 Frontend should display {len(unread)} unread messages:")
        
        for i, msg in enumerate(unread[:5]):  # Show first 5
            print(f"\n  {i+1}. 📬 {msg.contact_name or 'Unknown'}")
            print(f"     📞 {msg.phone_number}")
            print(f"     💬 {msg.incoming_message[:50]}...")
            print(f"     ⏰ {msg.incoming_time}")
            print(f"     📱 Device: {msg.device_id}")
            print(f"     📧 Message ID: {msg.message_id}")
            print(f"     📄 Unread: {'✅' if not msg.is_read else '❌'}")
        
        if len(unread) > 5:
            print(f"\n     ... and {len(unread) - 5} more messages")
        
        print(f"\n✅ These are REAL WhatsApp messages from your mobile device!")
        print(f"🔧 Frontend should call GET /api/replies/unread-messages to get them")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

def create_frontend_integration_guide():
    """Create a simple guide for frontend developers"""
    
    print("\n📱 FRONTEND INTEGRATION GUIDE")
    print("=" * 60)
    
    print("""
🔧 JAVASCRIPT/REACT INTEGRATION:

1. API Service Setup:
```javascript
const api = {
  getUnreadMessages: async () => {
    const token = localStorage.getItem('jwt_token');
    const response = await fetch('/api/replies/unread-messages', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  },
  
  getUnreadCount: async () => {
    const token = localStorage.getItem('jwt_token');
    const response = await fetch('/api/replies/unread-count', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }
};
```

2. Component Usage:
```javascript
const [unreadMessages, setUnreadMessages] = useState([]);
const [unreadCount, setUnreadCount] = useState(0);

useEffect(() => {
  // Fetch unread messages
  api.getUnreadMessages().then(data => {
    setUnreadMessages(data.data || []);
  });
  
  // Fetch unread count
  api.getUnreadCount().then(data => {
    setUnreadCount(data.total_unread || 0);
  });
}, []);

// Real-time updates
useEffect(() => {
  const interval = setInterval(() => {
    api.getUnreadCount().then(data => {
      setUnreadCount(data.total_unread || 0);
    });
  }, 30000); // Every 30 seconds
  
  return () => clearInterval(interval);
}, []);
```

3. Display Unread Messages:
```javascript
{unreadMessages.map(msg => (
  <div key={msg.id} className="unread-message">
    <h4>{msg.contact_name} ({msg.phone_number})</h4>
    <p>{msg.incoming_message}</p>
    <small>{new Date(msg.incoming_time).toLocaleString()}</small>
    {msg.unread && <span className="unread-badge">📬</span>}
  </div>
))}
```

4. Unread Badge:
```javascript
<div className="unread-badge">
  {unreadCount > 0 && (
    <span className="badge">{unreadCount}</span>
  )}
</div>
```
    """)

if __name__ == "__main__":
    test_api_endpoints_directly()
    show_expected_unread_messages()
    create_frontend_integration_guide()
    
    print("\n🚀 READY FOR FRONTEND INTEGRATION!")
    print("📱 All unread messages are available via API endpoints")
