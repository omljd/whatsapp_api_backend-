import requests
import sys
import os
from datetime import timedelta

# Add backend to sys.path
sys.path.append(os.getcwd())

from core.security import create_access_token

BASE_URL = "http://127.0.0.1:8000/api/admin/plans"

def test_plans_listing(role, user_id, email, category=None):
    print(f"\n--- Testing Plans Listing for {role.upper()} (category={category}) ---")
    token = create_access_token(
        data={"sub": str(user_id), "email": email, "role": role},
        expires_delta=timedelta(minutes=30)
    )
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"category": category} if category else {}
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            plans = response.json()
            print(f"Success! Retrieved {len(plans)} plans.")
            if len(plans) > 0:
                print(f"Example Plan: {plans[0]['name']} (Category: {plans[0]['plan_category']})")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")

def test_unauthorized_post(role, user_id, email):
    print(f"\n--- Testing Unauthorized POST for {role.upper()} ---")
    token = create_access_token(
        data={"sub": str(user_id), "email": email, "role": role},
        expires_delta=timedelta(minutes=30)
    )
    headers = {"Authorization": f"Bearer {token}"}
    dummy_plan = {
        "name": "Hack Plan",
        "price": 0,
        "credits_offered": 100,
        "validity_days": 30,
        "deduction_value": 0.5,
        "plan_category": "BUSINESS"
    }
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=dummy_plan)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 403:
            print("Successfully blocked unauthorized plan creation! (403 Forbidden)")
        else:
            print(f"WARNING: Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    # Real IDs from previous DB lookup
    admin_id = "62f6bb0e-c4ed-4b0c-856f-765d17327be2"
    reseller_id = "297d7e44-6e90-4891-b46f-74bdf0fa238b"
    user_id = "f017b7ed-cf4a-40b3-88ae-682a3b23d541"
    
    # Verify GET works for all
    test_plans_listing("admin", admin_id, "adminlogin6631@gmail.com")
    test_plans_listing("reseller", reseller_id, "sharad.pawar@example.com", category="BUSINESS")
    test_plans_listing("user", user_id, "rohit.hol01@gmail.com", category="BUSINESS")
    
    # Verify POST is still restricted for non-admins
    test_unauthorized_post("reseller", reseller_id, "sharad.pawar@example.com")
    test_unauthorized_post("user", user_id, "rohit.hol01@gmail.com")
