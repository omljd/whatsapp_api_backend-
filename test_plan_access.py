import requests
import sys
import os
from datetime import timedelta

# Add the backend path to sys.path to import core.security
sys.path.append(os.path.join(os.getcwd()))

try:
    from core.security import create_access_token
except ImportError:
    print(f"Could not import create_access_token. Current CWD: {os.getcwd()}")
    sys.exit(1)

BASE_URL = "http://127.0.0.1:8000/api/busi_users/me/plan"

def test_role(role, user_id, email):
    print(f"\n--- Testing Role: {role} (ID: {user_id}) ---")
    token = create_access_token(
        data={"sub": str(user_id), "email": email, "role": role},
        expires_delta=timedelta(minutes=30)
    )
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(BASE_URL, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"User Type: {data.get('user_type')}")
            print(f"Plan Name: {data.get('plan_name')}")
            print(f"Credits Remaining: {data.get('credits_remaining')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    print("Running integration tests against live server...")
    
    # Using real IDs found in DB
    # Admin: 62f6bb0e-c4ed-4b0c-856f-765d17327be2 adminlogin6631@gmail.com
    # Reseller: 297d7e44-6e90-4891-b46f-74bdf0fa238b sharad.pawar@example.com
    # BusiUser: f017b7ed-cf4a-40b3-88ae-682a3b23d541 rohit.hol01@gmail.com
    
    test_role("admin", "62f6bb0e-c4ed-4b0c-856f-765d17327be2", "adminlogin6631@gmail.com")
    test_role("reseller", "297d7e44-6e90-4891-b46f-74bdf0fa238b", "sharad.pawar@example.com")
    test_role("user", "f017b7ed-cf4a-40b3-88ae-682a3b23d541", "rohit.hol01@gmail.com")
