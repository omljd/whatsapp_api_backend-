#!/usr/bin/env python3

"""
Test login endpoints to verify they're working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

def test_login_endpoints():
    """Test both reseller and business login endpoints"""
    
    print("🔍 Testing Login Endpoints")
    print("=" * 50)
    
    # Test 1: Check if endpoints exist
    print("\n1. Testing endpoint existence:")
    
    try:
        # Test reseller login endpoint
        response = client.options("/api/resellers/login")
        print(f"   Reseller login OPTIONS: {response.status_code}")
        
        # Test business login endpoint  
        response = client.options("/api/busi_users/login")
        print(f"   Business login OPTIONS: {response.status_code}")
        
    except Exception as e:
        print(f"   Error checking endpoints: {e}")
    
    # Test 2: Test with invalid credentials
    print("\n2. Testing with invalid credentials:")
    
    try:
        # Test reseller login
        response = client.post("/api/resellers/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        print(f"   Reseller login status: {response.status_code}")
        print(f"   Reseller login response: {response.json()}")
        
        # Test business login
        response = client.post("/api/busi_users/login", json={
            "email": "invalid@test.com", 
            "password": "wrongpassword"
        })
        print(f"   Business login status: {response.status_code}")
        print(f"   Business login response: {response.json()}")
        
    except Exception as e:
        print(f"   Error testing login: {e}")
    
    # Test 3: Check API base URL
    print("\n3. Testing API base URL:")
    
    try:
        response = client.get("/api/")
        print(f"   API root status: {response.status_code}")
        
    except Exception as e:
        print(f"   Error testing API root: {e}")
    
    # Test 4: Check FastAPI routes
    print("\n4. Checking FastAPI routes:")
    
    try:
        from main import app
        login_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                if 'login' in route.path:
                    login_routes.append(f"{list(route.methods)} {route.path}")
        
        print("   Login routes found:")
        for route in sorted(login_routes):
            print(f"     {route}")
            
    except Exception as e:
        print(f"   Error checking routes: {e}")
    
    print("\n5. Common login issues:")
    print("   - Backend server not running")
    print("   - API URL mismatch between frontend and backend")
    print("   - CORS issues")
    print("   - Database connection problems")
    print("   - Invalid credentials")
    
    print("\n6. Frontend troubleshooting:")
    print("   - Check browser console for errors")
    print("   - Check network tab for failed requests")
    print("   - Verify API_BASE_URL in config/api.ts")
    print("   - Check localStorage for tokens")

if __name__ == "__main__":
    test_login_endpoints()
