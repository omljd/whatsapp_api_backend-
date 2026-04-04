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
SHEET_ID = "57dcde81-3352-4071-a105-491eec99ba30"
DEVICE_IDS = ["2f8aca4f-f444-430c-ace9-71ce487be2c2", "c73ff0c2-37f5-4422-9c34-a26f1255eb86"]

async def run_final_real_test():
    print("="*60)
    print("🚀 STARTING FINAL REAL PRODUCTION TEST")
    print(f"📧 User: {EMAIL}")
    print(f"📄 Sheet ID: {SHEET_ID}")
    print("="*60)

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Login
        print("\n🔐 [STEP 1] Authenticaticating...")
        try:
            # Note: Path is /api/busi_users/login
            login_payload = {"email": EMAIL, "password": PASSWORD}
            # Prefix is /api/busi_users in main.py? Let's check. 
            # busi_user.py has prefix /busi_users. main.py includes it with /api.
            res = await client.post(f"{BASE_URL}/busi_users/login", json=login_payload)
            if res.status_code != 200:
                print(f"❌ Login failed ({res.status_code}): {res.text}")
                return
            
            auth_data = res.json()
            token = auth_data.get("access_token")
            if not token:
                print(f"❌ Token missing in response.")
                return
                
            print("✅ Login Successful!")
            headers = {"Authorization": f"Bearer {token}"}
        except Exception as e:
            print(f"❌ Login error: {e}")
            return

        # 2. Create Campaign
        print("\n🚀 [STEP 2] Creating Campaign...")
        try:
            campaign_payload = {
                "sheet_id": SHEET_ID,
                "name": f"Real Test {datetime.now().strftime('%H:%M:%S')}",
                "device_ids": DEVICE_IDS,
                "templates": [
                    {"content": "Hi! This is test message 1 for campaign test. Status: {{Status}}"},
                    {"content": "Test 2: Hope you are doing well!"},
                ],
                "warm_mode": False
            }
            
            res = await client.post(f"{BASE_URL}/campaign/create", json=campaign_payload, headers=headers)
            if res.status_code not in [200, 210, 201]:
                print(f"❌ Campaign creation failed ({res.status_code}): {res.text}")
                return
                
            campaign_data = res.json()
            # The response structure might be wrapped in "data" or "result"
            if "id" in campaign_data:
                 campaign_id = campaign_data["id"]
            elif "data" in campaign_data and "id" in campaign_data["data"]:
                 campaign_id = campaign_data["data"]["id"]
            else:
                 print(f"❌ Could not find campaign ID in: {json.dumps(campaign_data)}")
                 return
                 
            print(f"✅ Campaign Created! ID: {campaign_id}")
        except Exception as e:
            print(f"❌ Campaign creation error: {e}")
            return

        # 3. Start Campaign
        print("\n⏯️ [STEP 3] Starting Campaign...")
        try:
            res = await client.post(f"{BASE_URL}/campaign/{campaign_id}/start", headers=headers)
            if res.status_code == 200:
                print("✅ Campaign START request accepted!")
            else:
                print(f"❌ Failed to start campaign: {res.text}")
                return
        except Exception as e:
            print(f"❌ Start error: {e}")
            return

        # 4. Monitor
        print("\n📊 [STEP 4] Monitoring progress (30s)...")
        await asyncio.sleep(30)
        
        # 5. Report Table
        print("\n" + "="*80)
        print(f"📢 FINAL DELIVERY REPORT (Campaign {campaign_id})")
        print("="*80)
        
        try:
            res_logs = await client.get(f"{BASE_URL}/campaign/{campaign_id}/logs", headers=headers)
            if res_logs.status_code == 200:
                logs_data = res_logs.json()
                logs = logs_data.get("logs", [])
                
                if not logs:
                    print("⚠️ No logs found yet. Campaign might be starting...")
                else:
                    print(f"{'#':<3} | {'Recipient':<15} | {'Status':<12} | {'Time':<20}")
                    print("-" * 80)
                    for i, log in enumerate(logs[:10], 1): # Show up to 10
                         recipient = log.get("recipient", "N/A")
                         status = log.get("status", "PENDING")
                         time = log.get("created_at", "N/A")
                         print(f"{i:<3} | {recipient:<15} | {status:<12} | {time:<20}")
            else:
                print(f"❌ Could not fetch logs: {res_logs.text}")
        except Exception as e:
            print(f"❌ Error fetching results: {e}")

        print("="*80)
        print("💡 NOTE: If status is 'Pending', ensure background tasks are enabled.")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(run_final_real_test())
