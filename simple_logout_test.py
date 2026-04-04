#!/usr/bin/env python3
"""
Simple test for device logout without complex setup
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_simple_logout():
    """Test simple device logout"""
    print("🧪 Testing simple device logout...")
    
    # Test with a fake device ID first
    fake_device_id = "550e8400-e29b-41d4-a716-446655449999"
    
    try:
        response = requests.delete(f"{BACKEND_URL}/api/devices/{fake_device_id}")
        print(f"   Response status: {response.status_code}")
        print(f"   Response body: {response.text}")
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent device")
            return True
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_simple_logout()
