#!/usr/bin/env python3
"""
Test the manual send endpoint fix
"""

import asyncio
import json
from fastapi.testclient import TestClient
from main import app

def test_manual_send():
    """Test manual send endpoint"""
    client = TestClient(app)
    
    print("🧪 Testing Manual Send Endpoint")
    print("=" * 50)
    
    # Test 1: Check if endpoint exists and accepts correct schema
    test_payload = {
        "device_id": "4337c1ea-29fe-4673-b7bd-0c4bffca4ec5",  # Valid device UUID
        "message_template": "Hello {name}, this is a test message.",
        "phone_column": "A",
        "send_all": True
    }
    
    try:
        response = client.post(
            "/api/google-sheets/test-sheet-id/manual-send",
            json=test_payload
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:
            print("❌ Still getting 422 error - validation issue")
            print(f"Response: {response.json()}")
            return False
        elif response.status_code == 401:
            print("⚠️  Auth required (expected)")
            print("✅ Endpoint accepts the schema - no 422 error!")
            return True
        elif response.status_code == 400:
            print("⚠️  Business logic error (sheet not found)")
            print("✅ Endpoint accepts the schema - no 422 error!")
            return True
        elif response.status_code == 200:
            print("✅ Success!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_schema_validation():
    """Test schema validation directly"""
    from schemas.google_sheet import ManualSendRequest
    
    print("\n🔍 Testing Schema Validation")
    print("=" * 50)
    
    # Test valid payload
    try:
        valid_payload = {
            "device_id": "4337c1ea-29fe-4673-b7bd-0c4bffca4ec5",
            "message_template": "Hello {name}",
            "phone_column": "A",
            "send_all": True
        }
        
        request = ManualSendRequest(**valid_payload)
        print("✅ Valid payload accepted")
        print(f"   Device ID: {request.device_id}")
        print(f"   Send All: {request.send_all}")
        print(f"   Selected Rows: {request.selected_rows}")
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False
    
    # Test payload with selected_rows
    try:
        payload_with_rows = {
            "device_id": "4337c1ea-29fe-4673-b7bd-0c4bffca4ec5",
            "message_template": "Hello {name}",
            "phone_column": "A",
            "selected_rows": [{"name": "John", "phone": "+1234567890"}],
            "send_all": False
        }
        
        request = ManualSendRequest(**payload_with_rows)
        print("✅ Payload with selected_rows accepted")
        print(f"   Selected Rows Count: {len(request.selected_rows)}")
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Manual Send Fix Verification")
    print("=" * 60)
    
    schema_ok = test_schema_validation()
    endpoint_ok = test_manual_send()
    
    print("\n" + "=" * 60)
    print("📋 Test Results:")
    print(f"   Schema Validation: {'✅ PASS' if schema_ok else '❌ FAIL'}")
    print(f"   Endpoint Test: {'✅ PASS' if endpoint_ok else '❌ FAIL'}")
    
    if schema_ok and endpoint_ok:
        print("\n🎉 Manual send fix is working!")
        print("   • No more 422 validation errors")
        print("   • Endpoint accepts both send_all and selected_rows")
        print("   • Ready for real testing with authenticated user")
    else:
        print("\n⚠️  Issues still exist - review above errors")
    
    print("=" * 60)
