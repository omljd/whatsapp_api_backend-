#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import uuid

# Create test client
client = TestClient(app)

def test_remove_action():
    """Test the remove action in POST contacts endpoint"""
    
    test_group_id = str(uuid.uuid4())
    test_phone = "1234567890"
    
    # Test remove action
    payload = {
        "action": "remove",
        "contacts": [
            {"phone": test_phone}
        ]
    }
    
    response = client.post(
        f"/api/groups/{test_group_id}/contacts",
        json=payload
    )
    
    print(f"Remove action - Status: {response.status_code}")
    print(f"Remove action - Response: {response.json()}")
    
    # Test add action (original functionality)
    add_payload = {
        "action": "add",
        "contacts": [
            {"name": "Test Contact", "phone": test_phone}
        ]
    }
    
    response = client.post(
        f"/api/groups/{test_group_id}/contacts",
        json=add_payload
    )
    
    print(f"Add action - Status: {response.status_code}")
    print(f"Add action - Response: {response.json()}")

if __name__ == "__main__":
    test_remove_action()
