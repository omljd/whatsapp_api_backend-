import sys
import time
import requests
from datetime import timedelta
import logging

from db.session import SessionLocal
from models.busi_user import BusiUser
from models.device import Device
from models.google_sheet import GoogleSheet
from models.campaign import Campaign, MessageLog
from core.security import create_access_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LIVE_TEST")

def run_live_test():
    db = SessionLocal()
    
    device_id_str = "f0c0959a-06a5-47d9-8852-cc977f8a9d42"
    spreadsheet_id = "1-6Iv7XupNuV2_o7wZLsrdY4hgEc5ao7TV9IJahju7BE"
    
    # 1. Verify Device
    device = db.query(Device).filter(Device.device_id == device_id_str).first()
    if not device:
        logger.error(f"Device {device_id_str} not found in DB!")
        return
        
    busi_user_id = str(device.busi_user_id)
    user = db.query(BusiUser).filter(BusiUser.busi_user_id == busi_user_id).first()
    logger.info(f"Found Device owned by User: {user.busi_user_id}")
    
    # 2. Verify or Insert Google Sheet
    sheet = db.query(GoogleSheet).filter(
        GoogleSheet.spreadsheet_id == spreadsheet_id,
        GoogleSheet.user_id == busi_user_id
    ).first()
    
    if not sheet:
        logger.info(f"Sheet {spreadsheet_id} not mapped for this user. Inserting it temporarily...")
        sheet = GoogleSheet(
            user_id=busi_user_id,
            sheet_name="Test Sheet",
            spreadsheet_id=spreadsheet_id,
            worksheet_name="Sheet1", # Default fallback name
            status="ACTIVE"
        )
        db.add(sheet)
        db.commit()
        db.refresh(sheet)
    
    sheet_internal_id = str(sheet.id)
    
    # 3. Generate Auth
    token = create_access_token(data={"sub": busi_user_id, "role": user.role}, expires_delta=timedelta(minutes=60))
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "http://localhost:8000"
    
    # 4. Create Campaign Request
    messages = ["test1", "test 2", "test 3", "test 4", "test5"]
    templates = [{"content": m, "delay_override": 5} for m in messages]
    
    logger.info("Calling /api/campaign/create ...")
    create_res = requests.post(
        f"{base_url}/api/campaign/create", 
        json={
            "name": "Live E2E Test Campaign",
            "device_ids": [device_id_str],
            "sheet_id": sheet_internal_id,
            "templates": templates,
            "warm_mode": False
        }, 
        headers=headers
    )
    
    if create_res.status_code != 200:
        logger.error(f"Failed to create campaign: {create_res.text}")
        return
        
    campaign_id = create_res.json()["id"]
    logger.info(f"✅ Campaign created successfully: {campaign_id}")
    
    # 5. Start Campaign
    logger.info("Calling /api/campaign/.../start ...")
    start_res = requests.post(f"{base_url}/api/campaign/{campaign_id}/start", headers=headers)
    
    if start_res.status_code != 200:
        logger.error(f"Failed to start campaign: {start_res.text}")
        return
        
    logger.info("✅ Campaign started! Messages are now dequeuing to WhatsApp via Unity Service.")
    
    # 6. Poll Status
    print("\n⏳ Polling campaign status...")
    while True:
        status_res = requests.get(f"{base_url}/api/campaign/{campaign_id}/status", headers=headers)
        if status_res.status_code != 200:
            break
            
        data = status_res.json()
        current_status = data["status"]
        sent = data["sent_count"]
        failed = data["failed_count"]
        total = data["total_recipients"]
        rem = data["remaining"]
        
        sys.stdout.write(f"\rStatus: {current_status} | Sent: {sent} | Failed: {failed} | Queued: {rem}/{total}")
        sys.stdout.flush()
        
        if current_status == "Completed" or (rem == 0 and current_status != "Running" and current_status != "Pending"):
            print("\n✅ Campaign Finished!")
            break
            
        time.sleep(3)
        
    # 7. Print Report
    print("\n### 📊 Live Campaign Message Report\n")
    print("| Recipient Phone | Status | Retry | Delay Used (sec) | Executed At |")
    print("|-----------------|--------|-------|------------------|-------------|")
    
    logs = db.query(MessageLog).filter(MessageLog.campaign_id == campaign_id).order_by(MessageLog.created_at.asc()).all()
    for l in logs:
        status_icon = "✅ Sent" if l.status == "success" else f"❌ {l.status}"
        print(f"| {l.recipient} | {status_icon} | {l.retry_count} | {l.response_time} | {l.created_at.strftime('%H:%M:%S')} |")
        
    db.close()

if __name__ == '__main__':
    run_live_test()
