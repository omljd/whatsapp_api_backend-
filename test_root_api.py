import requests
try:
    url = "http://127.0.0.1:8000/"
    print(f"Checking {url}...")
    res = requests.get(url, timeout=2)
    print(f"Status: {res.status_code}")
except Exception as e:
    print(f"ERROR: {e}")
