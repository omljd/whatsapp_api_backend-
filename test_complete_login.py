#!/usr/bin/env python3

"""
Complete test of business user login flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import json

# Create test client
client = TestClient(app)

def test_complete_login():
    """Test the complete business user login flow"""
    
    print("🔍 Testing Complete Business User Login Flow")
    print("=" * 50)
    
    # Test 1: Check if login endpoint exists
    print("\n1. Testing login endpoint existence:")
    
    try:
        response = client.post("/api/busi_users/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 401:
            print("   ✅ Login endpoint exists and working (401 for invalid credentials)")
        elif response.status_code == 500:
            print("   ❌ Server error - checking details...")
            print(f"   Full response: {response.text}")
        else:
            print(f"   Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Check if we can create a test user
    print("\n2. Testing user creation:")
    
    try:
        # Try to create a test business user
        create_response = client.post("/api/busi_users/register", json={
            "parent_reseller_id": str(uuid.uuid4()),  # Random reseller ID
            "profile": {
                "name": "Test User",
                "username": "testuser",
                "email": "test@example.com",
                "phone": "1234567890",
                "password": "testpassword"
            },
            "business": {
                "business_name": "Test Business"
            }
        })
        print(f"   Create user status: {create_response.status_code}")
        
        if create_response.status_code == 201:
            print("   ✅ Test user created successfully")
            user_data = create_response.json()
            
            # Now try to login with the created user
            print("\n3. Testing login with created user:")
            
            login_response = client.post("/api/busi_users/login", json={
                "email": "test@example.com",
                "password": "testpassword"
            })
            
            print(f"   Login status: {login_response.status_code}")
            print(f"   Login response: {login_response.json()}")
            
            if login_response.status_code == 200:
                print("   ✅ Login successful!")
                tokens = login_response.json()
                print(f"   Access token: {tokens.get('access_token', 'N/A')[:50]}...")
                print(f"   Busi user ID: {tokens.get('busi_user', {}).get('busi_user_id', 'N/A')}")
                print(f"   User role: {tokens.get('busi_user', {}).get('role', 'N/A')}")
            else:
                print(f"   Login failed: {login_response.json()}")
                
        elif create_response.status_code == 400:
            print("   ⚠️  User creation failed (validation error)")
            print(f"   Response: {create_response.json()}")
        else:
            print(f"   Unexpected create status: {create_response.status_code}")
            print(f"   Response: {create_response.json()}")
            
    except Exception as e:
        print(f"   Error in user creation: {e}")
    
    # Test 3: Check database connection
    print("\n4. Testing database connection:")
    
    try:
        # Try to get all users
        users_response = client.get("/api/busi_users/")
        print(f"   Get users status: {users_response.status_code}")
        
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"   Total users: {len(users)}")
            if users:
                print(f"   Sample user: {users[0].get('profile', {}).get('email', 'N/A')}")
        else:
            print(f"   Error getting users: {users_response.json()}")
            
    except Exception as e:
        print(f"   Error checking database: {e}")
    
    # Test 4: Check token creation
    print("\n5. Testing token creation:")
    
    try:
        from utils.auth import create_access_token, create_refresh_token
        import uuid
        
        test_user_id = str(uuid.uuid4())
        access_token = create_access_token(
            data={"sub": test_user_id, "email": "test@example.com", "role": "user"}
        )
        refresh_token = create_refresh_token(
            data={"sub": test_user_id, "email": "test@example.com", "role": "user"}
        )
        
        print(f"   ✅ Access token created: {len(access_token)} characters")
        print(f"   ✅ Refresh token created: {len(refresh_token)} characters")
        
    except Exception as e:
        print(f"   ❌ Token creation error: {e}")
    
    print("\n6. Frontend Integration Issues:")
    print("   Common frontend problems:")
    print("   - API URL mismatch (frontend using production, backend local)")
    print("   - CORS configuration issues")
    print("   - Token storage problems in localStorage")
    print("   - Form validation errors")
    print("   - Network connectivity issues")
    
    print("\n7. Troubleshooting Steps:")
    print("   1. Check browser console for JavaScript errors")
    print("   2. Check network tab for failed requests")
    print("   3. Verify API_BASE_URL in frontend config")
    print("   4. Check localStorage for tokens after login")
    print("   5. Test with valid credentials")

if __name__ == "__main__":
    import uuid
    test_complete_login()
