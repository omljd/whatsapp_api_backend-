#!/usr/bin/env python3
"""
Test all Google Sheets API endpoints
"""

import requests
import json

def test_endpoint(url, description):
    """Test a single endpoint"""
    print(f"\n📡 Testing: {url}")
    print(f"📝 Description: {description}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ SUCCESS: {len(str(data))} characters")
                if 'data' in data and isinstance(data['data'], list):
                    print(f"📊 Records: {len(data['data'])}")
            except:
                print(f"✅ SUCCESS: {response.text[:100]}...")
        elif response.status_code == 404:
            print(f"❌ NOT FOUND: {response.text}")
        elif response.status_code == 400:
            print(f"❌ BAD REQUEST: {response.text}")
        elif response.status_code == 401:
            print(f"🔒 UNAUTHORIZED: Authentication required")
        else:
            print(f"❌ ERROR: {response.text}")
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

def main():
    """Test all endpoints"""
    print("🧪 TESTING ALL GOOGLE SHEETS API ENDPOINTS")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/google-sheets"
    
    endpoints = [
        (f"{base_url}/", "List all sheets"),
        (f"{base_url}/triggers/history/test", "Test trigger history (no auth)"),
        (f"{base_url}/triggers/history", "Trigger history (auth required)"),
        (f"{base_url}/docs", "API documentation"),
    ]
    
    for url, desc in endpoints:
        test_endpoint(url, desc)
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    print("✅ Working endpoints should return 200")
    print("❌ 404 = Endpoint not found")
    print("❌ 400 = Bad request (missing params)")
    print("🔒 401 = Authentication required")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Check if endpoints are registered in router")
    print("2. Verify backend startup logs for route registration")
    print("3. Check for import errors in google_sheets.py")

if __name__ == "__main__":
    main()
