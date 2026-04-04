import uuid
import sys
import requests
from datetime import timedelta
from core.security import create_access_token
from db.session import SessionLocal
from models.busi_user import BusiUser

db = SessionLocal()
existing_user = db.query(BusiUser).first()
if not existing_user:
    print("❌ No existing BusiUser found in database. Cannot test authenticated endpoints.")
    sys.exit(1)

token = create_access_token(data={"sub": str(existing_user.busi_user_id), "role": existing_user.role}, expires_delta=timedelta(minutes=60))

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": f"Bearer {token}"}

results = []
def log_result(endpoint, method, test_case, expected, actual):
    status = "✅ Pass" if expected == actual else "❌ Fail"
    results.append({
        "Endpoint": endpoint,
        "Method": method,
        "Test Case": test_case,
        "Expected": expected,
        "Actual": actual,
        "Status": status
    })

def check_500(res, endpoint):
    if res.status_code == 500:
        print(f"Server 500 on {endpoint}: {res.text}")

def run_all_tests():    
    # Generate UUIDs
    fake_camp_id = str(uuid.uuid4())
    fake_sheet_id = str(uuid.uuid4())

    # 1. Create Campaign
    req = {
        "name": "Test Campaign",
        "device_ids": ["dev_1"],
        "sheet_id": fake_sheet_id,
        "templates": [{"content": "Hello", "delay_override": 5}],
        "warm_mode": False
    }
    res = requests.post(f"{BASE_URL}/api/campaign/create", json=req, headers=HEADERS)
    log_result("/api/campaign/create", "POST", "Device not found/unauth", 400, res.status_code)
    
    req_invalid = {
        "name": "Test", "device_ids": ["1","2","3","4","5","6"], "sheet_id": fake_sheet_id, "templates": [], "warm_mode": False
    }
    res = requests.post(f"{BASE_URL}/api/campaign/create", json=req_invalid, headers=HEADERS)
    log_result("/api/campaign/create", "POST", "Validation: > 5 devices", 400, res.status_code)

    # 2. Start Campaign
    res = requests.post(f"{BASE_URL}/api/campaign/{fake_camp_id}/start", headers=HEADERS)
    check_500(res, "/start")
    log_result("/api/campaign/{id}/start", "POST", "Campaign Not Found", 404, res.status_code)

    res = requests.post(f"{BASE_URL}/api/campaign/invalid-uuid/start", headers=HEADERS)
    check_500(res, "/start invalid")
    log_result("/api/campaign/{id}/start", "POST", "Invalid UUID Format", 400, res.status_code)

    # 3. Pause
    res = requests.post(f"{BASE_URL}/api/campaign/{fake_camp_id}/pause", headers=HEADERS)
    check_500(res, "/pause")
    log_result("/api/campaign/{id}/pause", "POST", "Campaign Not Found", 404, res.status_code)

    # 4. Resume
    res = requests.post(f"{BASE_URL}/api/campaign/{fake_camp_id}/resume", headers=HEADERS)
    check_500(res, "/resume")
    log_result("/api/campaign/{id}/resume", "POST", "Campaign Not Found", 404, res.status_code)

    # 5. Status
    res = requests.get(f"{BASE_URL}/api/campaign/{fake_camp_id}/status", headers=HEADERS)
    check_500(res, "/status")
    log_result("/api/campaign/{id}/status", "GET", "Campaign Not Found", 404, res.status_code)

    # 6. Logs
    res = requests.get(f"{BASE_URL}/api/campaign/{fake_camp_id}/logs", headers=HEADERS)
    check_500(res, "/logs")
    log_result("/api/campaign/{id}/logs", "GET", "Campaign Not Found", 404, res.status_code)
    
    # 7 Websocket
    # Can test websocket connection rejection or just HTTP endpoints. 

    print("\n### 📊 Campaign API Test Report\n")
    print("| Endpoint | Method | Test Case | Expected Code | Actual Code | Status |")
    print("|----------|--------|-----------|---------------|-------------|--------|")
    for r in results:
        print(f"| `{r['Endpoint']}` | {r['Method']} | {r['Test Case']} | {r['Expected']} | {r['Actual']} | {r['Status']} |")

if __name__ == '__main__':
    run_all_tests()
