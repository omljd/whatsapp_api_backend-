#!/usr/bin/env python3
"""
Test direct engine communication using exact curl format
"""

import requests
import json
import time

def test_direct_engine():
    """Test direct engine communication"""
    
    device_id = "1d7a7df0-c8cc-4e22-b219-e45dbd65f2f0"
    url = f"http://localhost:3001/session/{device_id}/message"
    
    payload = {
        "to": "+1234567890",
        "message": f"Direct test message at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Testing direct engine communication...")
    print(f"   URL: {url}")
    print(f"   Payload: {payload}")
    print(f"   Headers: {headers}")
    
    try:
        # Use the exact same parameters as curl
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60  # 60 second timeout
        )
        
        print(f"✅ Response received!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🎉 SUCCESS! Message sent with ID: {result.get('messageId')}")
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout as e:
        print(f"⏰ TIMEOUT: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_direct_engine()
    if success:
        print("\n✅ Direct engine test PASSED!")
    else:
        print("\n❌ Direct engine test FAILED!")
