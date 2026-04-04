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

def test_delete_by_phone():
    """Test delete by phone number"""
    
    test_group_id = str(uuid.uuid4())
    test_phone = "1234567890"
    
    # Test delete by phone number
    response = client.request(
        "DELETE",
        f"/api/groups/{test_group_id}/contacts",
        json={"phone": test_phone}
    )
    
    print(f"Delete by phone - Status: {response.status_code}")
    print(f"Delete by phone - Response: {response.json()}")
    
    # Test delete by contact_id
    test_contact_id = str(uuid.uuid4())
    response = client.request(
        "DELETE",
        f"/api/groups/{test_group_id}/contacts",
        json={"contact_id": test_contact_id}
    )
    
    print(f"Delete by contact_id - Status: {response.status_code}")
    print(f"Delete by contact_id - Response: {response.json()}")

if __name__ == "__main__":
    test_delete_by_phone()
