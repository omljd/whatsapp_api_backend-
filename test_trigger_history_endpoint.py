#!/usr/bin/env python3
"""
Test the trigger history endpoint
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_trigger_history_endpoint():
    """Test the trigger history endpoint"""
    
    print("🧪 TESTING TRIGGER HISTORY ENDPOINT")
    print("=" * 50)
    
    # Test endpoint
    url = "http://localhost:8000/api/google-sheets/triggers/history"
    
    try:
        print(f"📡 Testing: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Endpoint working!")
            try:
                data = response.json()
                print(f"📄 Response Data: {json.dumps(data, indent=2)}")
            except:
                print(f"📄 Raw Response: {response.text}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend is not running")
        print("💡 Please start the backend with: uvicorn main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_backend_running():
    """Test if backend is running"""
    
    print("\n🔍 CHECKING BACKEND STATUS")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print("❌ Backend not responding correctly")
            return False
    except:
        print("❌ Backend is not running")
        return False

def main():
    """Main test function"""
    print("🚀 TRIGGER HISTORY ENDPOINT TEST")
    
    # Check if backend is running
    if test_backend_running():
        # Test the endpoint
        test_trigger_history_endpoint()
    else:
        print("\n📝 SOLUTION:")
        print("1. Start the backend:")
        print("   uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        print("2. Then run this test again")
        print("3. Check the backend logs for any errors")

if __name__ == "__main__":
    main()
