#!/usr/bin/env python3

"""
Test delete sheet with proper authentication simulation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import uuid
import json

# Create test client
client = TestClient(app)

def test_delete_with_debug():
    """Test delete with detailed debugging"""
    
    print("🔍 Testing Google Sheet Delete with Authentication")
    print("=" * 50)
    
    # First, let's test the endpoint structure
    print("\n1. Testing endpoint structure:")
    
    try:
        # Try to get the sheets list first
        response = client.get("/api/google-sheets/")
        print(f"   GET sheets status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Authentication required (expected)")
        else:
            print(f"   Response: {response.json()}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test delete with a valid UUID but no auth
    print("\n2. Testing DELETE without authentication:")
    
    test_uuid = str(uuid.uuid4())
    try:
        response = client.delete(f"/api/google-sheets/{test_uuid}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 500:
            print("   ❌ 500 Error - this indicates a server issue")
            print("   The endpoint exists but has an internal error")
            
            # Try to get more error details
            if hasattr(response, 'text'):
                print(f"   Full response: {response.text}")
                
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if the endpoint is properly registered
    print("\n3. Checking FastAPI routes:")
    
    try:
        from main import app
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                if 'google-sheets' in route.path:
                    routes.append(f"{list(route.methods)} {route.path}")
        
        print("   Google Sheets routes:")
        for route in sorted(routes):
            print(f"     {route}")
            
        # Check if DELETE route exists
        delete_route_exists = any('DELETE' in route and '/{sheet_id}' in route for route in routes)
        if delete_route_exists:
            print("   ✅ DELETE route exists")
        else:
            print("   ❌ DELETE route missing")
            
    except Exception as e:
        print(f"   Error checking routes: {e}")
    
    print("\n4. Possible causes of 500 error:")
    print("   - Database connection issues")
    print("   - Missing imports in google_sheets.py")
    print("   - SQL syntax errors")
    print("   - Transaction handling issues")
    print("   - Missing database tables")
    
    print("\n5. Next steps:")
    print("   - Check backend logs for detailed error")
    print("   - Verify database connection")
    print("   - Test with a real sheet ID")
    print("   - Check if all imports are correct")

if __name__ == "__main__":
    test_delete_with_debug()
