#!/usr/bin/env python3
"""
Test manual send with debug logging enabled
"""

from fastapi.testclient import TestClient
from main import app
import json

def test_manual_send_with_debug():
    """Test manual send endpoint with debug logging"""
    client = TestClient(app)
    
    print("🔍 Testing Manual Send with Debug Logging")
    print("=" * 60)
    
    sheet_id = 'e97846dd-62f0-407b-9ad9-417463d5f1d1'
    
    # Test cases that might cause 422
    test_cases = [
        {
            "name": "Standard payload",
            "payload": {
                "device_id": "4337c1ea-29fe-4673-b7bd-0c4bffca4ec5",
                "message_template": "Hello {name}",
                "phone_column": "A",
                "send_all": True
            }
        },
        {
            "name": "Empty payload",
            "payload": {}
        },
        {
            "name": "Missing required fields",
            "payload": {
                "device_id": "4337c1ea-29fe-4673-b7bd-0c4bffca4ec5"
            }
        },
        {
            "name": "Null values",
            "payload": {
                "device_id": None,
                "message_template": None,
                "phone_column": None,
                "send_all": True
            }
        },
        {
            "name": "Wrong data types",
            "payload": {
                "device_id": 123,  # number instead of string
                "message_template": ["Hello"],  # array instead of string
                "phone_column": {"col": "A"},  # object instead of string
                "send_all": "true"  # string instead of boolean
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Payload: {json.dumps(test_case['payload'], indent=4)}")
        
        try:
            response = client.post(
                f'/api/google-sheets/{sheet_id}/manual-send',
                json=test_case['payload']
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 422:
                print(f"   ❌ 422 Error Details:")
                print(f"   {json.dumps(response.json(), indent=6)}")
            elif response.status_code == 401:
                print(f"   ✅ Auth required (no 422!)")
            elif response.status_code == 400:
                print(f"   ⚠️  Business logic error: {response.json()}")
            else:
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("📋 Debug Test Complete")

if __name__ == "__main__":
    test_manual_send_with_debug()
