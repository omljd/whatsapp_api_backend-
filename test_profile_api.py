import requests
try:
    url = "http://127.0.0.1:8000/api/resellers/me"
    print(f"Checking {url}...")
    res = requests.get(url, timeout=5)
    print(f"Status: {res.status_code}")
    print(f"Body: {res.text}")
except Exception as e:
    print(f"NETWORK ERROR: {e}")
