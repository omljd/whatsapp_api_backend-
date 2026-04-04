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

def test_delete_contact_api():
    print("Testing DELETE contact from group API...")
    
    # Test the API endpoint exists
    response = client.options("/api/groups/test-group-id/contacts")
    print(f"OPTIONS response status: {response.status_code}")
    
    # Test delete with sample data
    test_group_id = str(uuid.uuid4())
    test_contact_id = str(uuid.uuid4())
    
    # Use the correct TestClient syntax
    response = client.delete(
        f"/api/groups/{test_group_id}/contacts",
        data=json.dumps({"contact_id": test_contact_id}),
        headers={"Content-Type": "application/json"}
    )
    
    print(f"DELETE response status: {response.status_code}")
    print(f"DELETE response body: {response.json()}")
    
    return response.status_code

if __name__ == "__main__":
    test_delete_contact_api()
