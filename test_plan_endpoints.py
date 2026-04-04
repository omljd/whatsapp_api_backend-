import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/busi_users"

def test_available_plans():
    print("Testing GET /plans/available...")
    try:
        response = requests.get(f"{BASE_URL}/plans/available")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Available plans:")
            print(response.json())
        else:
            print(f"Failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_me_plan_no_auth():
    print("\nTesting GET /me/plan without auth (should be 401)...")
    try:
        response = requests.get(f"{BASE_URL}/me/plan")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_available_plans()
    test_me_plan_no_auth()
