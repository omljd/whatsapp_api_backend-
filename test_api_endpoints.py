import requests
import json
import logging

BASE_URL = "http://localhost:8000"

endpoints = [
    "/health",
    "/api/reseller/analytics",
    "/api/busi_users/analytics",
    "/api/webhooks/whatsapp/incoming",
]

def test_endpoints():
    print(f"Testing endpoints on {BASE_URL}...")
    for ep in endpoints:
        url = f"{BASE_URL}{ep}"
        try:
            # Most of these need auth, so we expect 401/403, but NOT 500
            response = requests.get(url, timeout=5)
            print(f"  {ep} -> {response.status_code}")
            if response.status_code == 500:
                 print(f"    🔥 500 ERROR FOUND! Response: {response.text}")
        except Exception as e:
            print(f"  {ep} -> FAILED: {str(e)}")

if __name__ == "__main__":
    test_endpoints()
