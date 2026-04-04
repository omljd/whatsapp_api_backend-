#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import uuid

# Create test client
client = TestClient(app)

def test_post_delete():
    """Test POST delete endpoint"""
    
    test_group_id = str(uuid.uuid4())
    test_phone = "1234567890"
    
    # Test POST delete by phone number
    response = client.post(
        f"/api/groups/{test_group_id}/contacts/delete",
        json={"phone": test_phone}
    )
    
    print(f"POST delete by phone - Status: {response.status_code}")
    print(f"POST delete by phone - Response: {response.json()}")
    
    # Test POST delete by contact_id
    test_contact_id = str(uuid.uuid4())
    response = client.post(
        f"/api/groups/{test_group_id}/contacts/delete",
        json={"contact_id": test_contact_id}
    )
    
    print(f"POST delete by contact_id - Status: {response.status_code}")
    print(f"POST delete by contact_id - Response: {response.json()}")

if __name__ == "__main__":
    test_post_delete()
