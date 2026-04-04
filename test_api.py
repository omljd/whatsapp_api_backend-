import os
import sys
import json
import requests
import time

sys.path.append('d:/BULK devlop/wh-api-backend-vikas')

# 1. Fetch data directly from DB
from db.session import SessionLocal
from models.busi_user import BusiUser
from models.google_sheet import GoogleSheet
from models.device import Device
from core.security import create_access_token

db = SessionLocal()
sheet = db.query(GoogleSheet).first()
if not sheet:
    print("No Google Sheet found in the database. Please create one first.")
    sys.exit(1)

user = db.query(BusiUser).filter(BusiUser.busi_user_id == sheet.user_id).first()
if not user:
    print("No BusiUser found for the sheet.")
    sys.exit(1)

print(f"Using test user: {user.email} (busi_user_id: {user.busi_user_id})")

try:
    token = create_access_token({'sub': str(user.busi_user_id)})
except Exception as e:
    print(f"Failed to create token natively: {e}")
    sys.exit(1)

print(f"Generated Token: {token[:20]}...")
print(f"Using Sheet ID: {sheet.id}")

device = db.query(Device).filter(Device.busi_user_id == user.busi_user_id, Device.is_active == True).first()
if not device:
    print("No active Device found for user.")
    sys.exit(1)
print(f"Using Device ID: {device.device_id}")

# 2. Simulate Frontend API calls
API_BASE_URL = "http://127.0.0.1:8000/api"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "sheet_id": str(sheet.id),
    "name": "Integration Test Campaign",
    "device_ids": [str(device.device_id)],
    "templates": [{"content": "Hello {Name}, this is a test from the UI script.", "delay_override": None}]
}

print("\n--- 1. Creating Campaign ---")
res = requests.post(f"{API_BASE_URL}/campaign/create", json=payload, headers=headers)
print(f"Status: {res.status_code}")
try:
    print(json.dumps(res.json(), indent=2))
    campaign_id = res.json().get("id")
except:
    print(res.text)
    sys.exit(1)

if not campaign_id:
    print("Failed to get campaign_id")
    sys.exit(1)

print("\n--- 2. Starting Campaign ---")
res = requests.post(f"{API_BASE_URL}/campaign/{campaign_id}/start", headers=headers)
print(f"Status: {res.status_code}")
try:
    print(json.dumps(res.json(), indent=2))
except:
    print(res.text)

print("\n--- 3. Checking Status ---")
res = requests.get(f"{API_BASE_URL}/campaign/{campaign_id}/status", headers=headers)
print(f"Status: {res.status_code}")
try:
    print(json.dumps(res.json(), indent=2))
except:
    print(res.text)

print("\n--- 4. Pausing Campaign ---")
res = requests.post(f"{API_BASE_URL}/campaign/{campaign_id}/pause", headers=headers)
print(f"Status: {res.status_code}")
try:
    print(json.dumps(res.json(), indent=2))
except:
    print(res.text)

print("\n--- 5. Resuming Campaign ---")
res = requests.post(f"{API_BASE_URL}/campaign/{campaign_id}/resume", headers=headers)
print(f"Status: {res.status_code}")
try:
    print(json.dumps(res.json(), indent=2))
except:
    print(res.text)

print("\n--- 6. Fetching Logs ---")
res = requests.get(f"{API_BASE_URL}/campaign/{campaign_id}/logs", headers=headers)
print(f"Status: {res.status_code}")
try:
    print(json.dumps(res.json(), indent=2))
except:
    print(res.text)

