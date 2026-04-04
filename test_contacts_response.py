#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import uuid
import json

# Create test client
client = TestClient(app)

def test_get_contacts_response():
    """Test what the get contacts endpoint returns"""
    
    # Test with a fake group ID to see the structure
    test_group_id = str(uuid.uuid4())
    
    response = client.get(f"/api/groups/{test_group_id}/contacts")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 404:
        print("Expected 404 for fake group ID")
    elif response.status_code == 200:
        contacts = response.json()
        if contacts:
            print(f"First contact structure: {contacts[0]}")
            if 'contact_id' in contacts[0]:
                print("✅ contact_id is present in response")
            else:
                print("❌ contact_id is missing from response")

if __name__ == "__main__":
    test_get_contacts_response()
