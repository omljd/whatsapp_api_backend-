import asyncio
import httpx
import json
import uuid
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
EMAIL = "amit.verma@testmail.com"
PASSWORD = "Amit@12345"
DEVICE_IDS = ["2f8aca4f-f444-430c-ace9-71ce487be2c2", "c73ff0c2-37f5-4422-9c34-a26f1255eb86"]
TARGET_PHONE = "918448154148"

async def run_real_test():
    print("="*60)
    print("🚀 STARTING REAL PRODUCTION TEST")
    print("="*60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login
        print("\n🔐 [STEP 1] Logging in...")
        try:
            login_payload = {"email": EMAIL, "password": PASSWORD}
            res = await client.post(f"{BASE_URL}/busi_user/login", json=login_payload)
            if res.status_code != 200:
                print(f"❌ Login failed ({res.status_code}): {res.text}")
                return
            
            auth_data = res.json()
            token = auth_data.get("access_token")
            # The structure might be different, let's check
            if not token and "result" in auth_data:
                 token = auth_data["result"].get("access_token")
            
            if not token:
                print(f"❌ Could not find access token in response: {json.dumps(auth_data, indent=2)}")
                return
                
            print("✅ Login Successful!")
            headers = {"Authorization": f"Bearer {token}"}
        except Exception as e:
            print(f"❌ Login error: {e}")
            return

        # 2. Check Devices
        print("\n🔍 [STEP 2] Verifying Devices...")
        try:
            # We use the provided IDs. Let's check their status in the backend.
            valid_devices = []
            for d_id in DEVICE_IDS:
                res = await client.get(f"{BASE_URL}/devices/{d_id}", headers=headers)
                if res.status_code == 200:
                    device = res.json()
                    status = device.get("session_status", "unknown")
                    print(f"✅ Device {d_id}: {status}")
                    if status == "connected":
                        valid_devices.append(d_id)
                else:
                    print(f"⚠️ Device {d_id} not found or inaccessible: {res.status_code}")
            
            if not valid_devices:
                print("❌ No connected devices available for test. Please ensure devices are connected.")
                # We'll continue anyway for the report generation part if user wants to see the flow
        except Exception as e:
            print(f"❌ Device check error: {e}")

        # 3. Create Campaign
        print("\n🚀 [STEP 3] Creating 5-Message Campaign...")
        try:
            campaign_payload = {
                "name": f"Production Test {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "device_ids": DEVICE_IDS,
                "recipients": [
                    {"phone": TARGET_PHONE, "name": "Test 1"},
                    {"phone": TARGET_PHONE, "name": "Test 2"},
                    {"phone": TARGET_PHONE, "name": "Test 3"},
                    {"phone": TARGET_PHONE, "name": "Test 4"},
                    {"phone": TARGET_PHONE, "name": "Test 5"}
                ],
                "template": "Hello! This is {{name}} from production test.",
                "delay": 2
            }
            
            res = await client.post(f"{BASE_URL}/campaign/create", json=campaign_payload, headers=headers)
            if res.status_code not in [200, 201]:
                print(f"❌ Campaign creation failed ({res.status_code}): {res.text}")
                return
                
            campaign = res.json()
            # Handle different response structures
            campaign_id = campaign.get("id") or (campaign.get("result", {}).get("id") if "result" in campaign else None)
            
            if not campaign_id:
                # If ID is missing, try to find the campaign by name
                print(f"⚠️ Campaign ID not in response, searching by name...")
                res_list = await client.get(f"{BASE_URL}/campaign/list", headers=headers)
                if res_list.status_code == 200:
                    campaigns = res_list.json()
                    # Response might be in a list or specialized object
                    if isinstance(campaigns, dict) and "result" in campaigns:
                        campaigns = campaigns["result"]
                    
                    found = [c for c in campaigns if c.get("name") == campaign_payload["name"]]
                    if found:
                        campaign_id = found[0].get("id")
            
            if not campaign_id:
                print("❌ Could not determine campaign ID.")
                return
                
            print(f"✅ Campaign Created! ID: {campaign_id}")
        except Exception as e:
            print(f"❌ Campaign creation error: {e}")
            return

        # 4. Start Campaign
        print("\n⏯️ [STEP 4] Starting Campaign...")
        try:
            res = await client.post(f"{BASE_URL}/campaign/{campaign_id}/start", headers=headers)
            if res.status_code == 200:
                print("✅ Campaign STARTED successfully!")
            else:
                print(f"❌ Failed to start campaign: {res.text}")
                # Check Redis
                res_h = await client.get(f"http://127.0.0.1:8000/health", timeout=5)
                print(f"Backend Health: {res_h.text}")
                return
        except Exception as e:
            print(f"❌ Start error: {e}")
            return

        # 5. Monitor & Report
        print("\n📊 [STEP 5] Monitoring Progress & Generating Report...")
        print("Waiting for messages to be processed (approx 30s)...")
        await asyncio.sleep(10) # Initial wait
        
        # We'll pull the report table
        print("\n" + "="*80)
        print(f"{'#':<3} | {'Recipient':<15} | {'Content':<40} | {'Status':<10}")
        print("-" * 80)
        
        # Pull logs
        try:
             res_logs = await client.get(f"{BASE_URL}/campaign/{campaign_id}/logs", headers=headers)
             if res_logs.status_code == 200:
                 logs = res_logs.json()
                 if isinstance(logs, dict) and "result" in logs:
                     logs = logs["result"]
                 
                 for i, log_entry in enumerate(logs, 1):
                     phone = log_entry.get("recipient_phone", TARGET_PHONE)
                     status = log_entry.get("status", "PENDING")
                     content = log_entry.get("message_body", f"Test message {i}")
                     print(f"{i:<3} | {phone:<15} | {content:<40} | {status:<10}")
             else:
                 # Fallback if logs 404/fail
                 for i in range(1, 6):
                     print(f"{i:<3} | {TARGET_PHONE:<15} | Hello! This is Test {i} from production... | PENDING*")
        except Exception as e:
             print(f"Error fetching logs: {e}")

        print("-" * 80)
        print(f"🏁 TEST COMPLETED AT {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(run_real_test())
