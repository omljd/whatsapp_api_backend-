#!/usr/bin/env python3
"""
Test device registration endpoint
"""
import requests
import json
import uuid

def test_device_registration():
    url = "http://localhost:8000/api/devices/register"
    
    payload = {
        "user_id": str(uuid.uuid4()),
        "device_name": "Test Device",
        "device_type": "web"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_device_registration()
