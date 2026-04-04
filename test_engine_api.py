import requests
import json
import time

BASE_URL = "http://localhost:3001"
DEVICE_ID = "test-manual-fix-1"

def test_engine():
    print(f"Testing Engine at {BASE_URL}")
    
    # 1. Health
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"Health: {r.status_code}")
        print(f"Headers: {r.headers}")
        print(f"Body: {r.text[:500]}") # Print first 500 chars
    except Exception as e:
        print(f"Health check failed: {e}")
        return

    # 2. Start Session
    print(f"\nAttempting to start session for {DEVICE_ID}...")
    try:
        # Try different common payloads/endpoints if one fails
        payloads = [
            {"sessionId": DEVICE_ID},
            {"id": DEVICE_ID}
        ]
        
        # Try /sessions (plural)
        print(f"POST /sessions with {payloads[1]}")
        try:
            r = requests.post(f"{BASE_URL}/sessions", json=payloads[1], timeout=5)
            print(f"Start Session (Plural): {r.status_code} {r.text}")
        except Exception as e:
            print(f"POST /sessions failed: {e}")

        # Try /sessions/add
        print(f"POST /sessions/add with {payloads[1]}")
        try:
            r = requests.post(f"{BASE_URL}/sessions/add", json=payloads[1], timeout=5)
            print(f"Start Session (Add): {r.status_code} {r.text}")
        except Exception as e:
            print(f"POST /sessions/add failed: {e}")

        for payload in payloads:
            print(f"POST /session with {payload}")
            r = requests.post(f"{BASE_URL}/session", json=payload, timeout=5)
            print(f"Start Session: {r.status_code} {r.text}")
            if r.status_code in [200, 201]:
                break
    except Exception as e:
        print(f"Start session failed: {e}")

    # 3. Get QR
    print(f"\nAttempting to get QR for {DEVICE_ID}...")
    try:
        r = requests.get(f"{BASE_URL}/session/{DEVICE_ID}/qr", timeout=5)
        print(f"Get QR: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            qr = data.get("qr") or data.get("qr_code")
            print(f"QR retrieved: {'Yes' if qr else 'No'} (Len: {len(qr) if qr else 0})")
            print(f"Full response: {data}")
    except Exception as e:
        print(f"Get QR failed: {e}")

if __name__ == "__main__":
    test_engine()
