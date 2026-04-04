#!/usr/bin/env python3

import sys
sys.path.append('.')

import requests
import json
from uuid import UUID

def test_with_mock_service():
    """Test the message flow with a mock WhatsApp service"""
    
    base_url = "http://127.0.0.1:8000/api"
    
    print("🧪 TESTING WITH MOCK WHATSAPP SERVICE")
    print("=" * 60)
    
    # Step 1: Login
    print("\n🔐 Step 1: Login")
    login_data = {
        "email": "amit.verma@testmail.com",
        "password": "Amit@12345"
    }
    
    try:
        response = requests.post(f"{base_url}/busi_users/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return False
            
        token_data = response.json()
        token = token_data.get("access_token")
        user_data = token_data.get("busi_user", {})
        
        print(f"✅ Login successful! User ID: {user_data.get('busi_user_id')}")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Step 2: Get Devices
        print("\n📱 Step 2: Get Devices")
        response = requests.get(f"{base_url}/whatsapp/devices", 
                              params={"user_id": str(user_data.get('busi_user_id'))}, 
                              headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            devices = response.json()
            print(f"✅ Found {len(devices)} devices")
            
            if not devices:
                print("❌ No devices found.")
                return False
                
            device = devices[0]
            print(f"   Using device: {device.get('device_name')} ({device.get('device_id')})")
            device_id = device.get('device_id')
        else:
            print(f"❌ Failed to get devices: {response.text}")
            return False
        
        # Step 3: Test Manual Send with valid phone numbers
        print("\n📤 Step 3: Test Manual Send")
        test_rows = [
            {"Phone": "+919876543210", "Name": "Test User", "Message": "Hello {{Name}}!", "Status": "Send"},
            {"Phone": "+919123456789", "Name": "Test User 2", "Message": "Hi {{Name}}!", "Status": "Send"}
        ]
        
        manual_send_data = {
            "device_id": device_id,
            "message_template": "Hello {{Name}}! This is a test message.",
            "phone_col": "Phone",
            "selected_rows": test_rows
        }
        
        print(f"   Sending {len(test_rows)} test messages...")
        print(f"   Device ID: {device_id}")
        print(f"   Template: {manual_send_data['message_template']}")
        
        # Test with shorter timeout to avoid hanging
        response = requests.post(f"{base_url}/google-sheets/send-manual", 
                               json=manual_send_data,
                               headers=headers,
                               timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Manual send API responded successfully!")
            print(f"   Result: {result}")
            
            # Check if we got a proper response structure
            if 'message' in result and 'sent' in result and 'failed' in result:
                print("✅ API response structure is correct")
                print(f"   Processed {len(test_rows)} rows")
                print(f"   Sent: {result.get('sent')}")
                print(f"   Failed: {result.get('failed')}")
                print(f"   Skipped: {result.get('skipped')}")
                
                if result.get('errors'):
                    print(f"   Errors: {result.get('errors')}")
                
                return True
            else:
                print("❌ API response structure is incorrect")
                return False
        else:
            print(f"❌ Manual send failed: {response.text}")
            return False
        
    except requests.exceptions.Timeout:
        print("❌ API is still hanging - timeout occurred")
        return False
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_mock_service()
    if success:
        print("\n🎉 MAIN ISSUE FIXED!")
        print("✅ API no longer hangs")
        print("✅ Frontend will receive proper responses")
        print("✅ 'Network Error (No Response)' issue resolved")
        print("\n📝 NEXT STEPS:")
        print("1. Fix WhatsApp Engine connection issues")
        print("2. Ensure device is properly connected to WhatsApp")
        print("3. Test with real WhatsApp numbers")
    else:
        print("\n❌ Still have issues to resolve")
    
    sys.exit(0 if success else 1)
