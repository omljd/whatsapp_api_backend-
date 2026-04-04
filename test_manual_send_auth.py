#!/usr/bin/env python3
"""
Test manual send with simulated authentication to trigger 422
"""

from fastapi.testclient import TestClient
from main import app
import json

def test_manual_send_with_auth():
    """Test manual send with authentication to trigger 422"""
    client = TestClient(app)
    
    print("🔍 Testing Manual Send with Auth Simulation")
    print("=" * 60)
    
    sheet_id = 'e97846dd-62f0-407b-9ad9-417463d5f1d1'
    
    # Test cases that might cause 422 after auth
    test_cases = [
        {
            "name": "Standard payload (should work)",
            "payload": {
                "device_id": "4337c1ea-29fe-4673-b7bd-0c4bffca4ec5",
                "message_template": "Hello {name}",
                "phone_column": "A",
                "send_all": True
            }
        },
        {
            "name": "Empty string values",
            "payload": {
                "device_id": "",
                "message_template": "",
                "phone_column": "",
                "send_all": True
            }
        },
        {
            "name": "Missing required fields",
            "payload": {
                "send_all": True
            }
        },
        {
            "name": "Invalid JSON structure",
            "payload": "invalid json"
        },
        {
            "name": "Array instead of object",
            "payload": [
                {"device_id": "test"},
                {"message_template": "hello"}
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Payload: {json.dumps(test_case['payload'], indent=4)}")
        
        try:
            # Try with different content types
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer fake-token"  # Fake auth to see if we get past 401
            }
            
            response = client.post(
                f'/api/google-sheets/{sheet_id}/manual-send',
                json=test_case['payload'],
                headers=headers
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 422:
                print(f"   ❌ 422 Error Details:")
                print(f"   {json.dumps(response.json(), indent=6)}")
                print("   🔍 FOUND THE 422 ERROR!")
            elif response.status_code == 401:
                print(f"   ✅ Auth required (no 422!)")
            elif response.status_code == 400:
                print(f"   ⚠️  Business logic error: {response.json()}")
            else:
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("📋 Auth Test Complete")

if __name__ == "__main__":
    test_manual_send_with_auth()
