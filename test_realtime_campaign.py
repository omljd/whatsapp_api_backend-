import asyncio
import time
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.busi_user import BusiUser
from models.device import Device
from models.google_sheet import GoogleSheet
from models.campaign import Campaign, MessageLog, CampaignStatus, MessageTemplate
from services.google_sheets_service import GoogleSheetsService
from services.unified_service import UnifiedWhatsAppService

async def main():
    db = SessionLocal()
    
    device_id = "f0c0959a-06a5-47d9-8852-cc977f8a9d42"
    spreadsheet_id = "1-6Iv7XupNuV2_o7wZLsrdY4hgEc5ao7TV9IJahju7BE"
    
    try:
        # Find device to infer user
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            print(f"Error: Device {device_id} not found in DB.")
            return
            
        busi_user_id = str(device.busi_user_id)
        print(f"Found device belonging to user: {busi_user_id}")
        
        # Check sheet
        sheet = db.query(GoogleSheet).filter(GoogleSheet.spreadsheet_id == spreadsheet_id).first()
        if not sheet:
            print(f"Error: Sheet with spreadsheet_id {spreadsheet_id} not found.")
            return
        
        # We will create a dummy campaign to attach logs to
        campaign = Campaign(busi_user_id=busi_user_id, sheet_id=sheet.id, status=CampaignStatus.RUNNING, name="Direct Realtime Test")
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        campaign_id = str(campaign.id)
        
        # Templates
        messages = ["test1", "test 2", "test 3", "test 4", "test5"]
        templates = []
        for msg in messages:
            mt = MessageTemplate(campaign_id=campaign.id, content=msg, delay_override=2)
            db.add(mt)
            templates.append(mt)
        db.commit()
        
        # Fetch data from sheet
        sheets_service = GoogleSheetsService()
        creds = sheets_service.get_service_account_credentials()
        
        rows_data, headers = sheets_service.get_sheet_data_with_headers(
            spreadsheet_id=sheet.spreadsheet_id, 
            worksheet_name=sheet.worksheet_name or "Sheet1",
            credentials=creds
        )
        
        formatted_rows = []
        phone_col = "phone"
        if sheet.trigger_config and isinstance(sheet.trigger_config, dict):
            phone_col = sheet.trigger_config.get("phone_column", phone_col)
            
        for row in rows_data:
            data = row.get("data", {})
            actual_phone = data.get(phone_col) or data.get("Phone") or data.get("Phone Number") or data.get("NUMBER")
            valid_phone = sheets_service.validate_phone_number(actual_phone)
            if valid_phone or actual_phone:
                formatted_rows.append({
                    "phone": valid_phone or actual_phone,
                    "row_data": data
                })
                
        if not formatted_rows:
            print("No valid rows found in sheet.")
            return
            
        print(f"Starting direct campaign with {len(formatted_rows)} recipients...")
        unified_service = UnifiedWhatsAppService(db)
        
        template_index = 0
        for i, recipient in enumerate(formatted_rows):
            phone = recipient["phone"]
            row_data = recipient.get("row_data", {})
            
            template = templates[template_index]
            template_index = (template_index + 1) % len(templates)
            
            content = template.content
            for key, val in row_data.items():
                content = content.replace(f"{{{key}}}", str(val))
                
            delay = template.delay_override or 2
            
            print(f"[{i+1}/{len(formatted_rows)}] Waiting {delay}s... Sending to {phone}: '{content}'")
            await asyncio.sleep(delay)
            
            success = False
            error_msg = None
            retry_count = 0
            
            while retry_count < 3 and not success:
                try:
                    result = await unified_service.send_message(
                        device_id=device_id,
                        to=phone,
                        message=content
                    )
                    if result.get("success"):
                        success = True
                    else:
                        error_msg = result.get("error", "Unknown erro")
                        retry_count += 1
                        print(f"  Retry {retry_count}/3 - Error: {error_msg}")
                        await asyncio.sleep(2)
                except Exception as e:
                    error_msg = str(e)
                    retry_count += 1
                    print(f"  Retry {retry_count}/3 - Exception: {error_msg}")
                    await asyncio.sleep(2)
                    
            # Save Log
            log_entry = MessageLog(
                campaign_id=campaign.id,
                device_id=device_id,
                recipient=phone,
                template_id=template.id,
                status="success" if success else f"failed: {error_msg}",
                retry_count=retry_count,
                response_time=delay
            )
            db.add(log_entry)
            
            if success:
                campaign.sent_count += 1
            else:
                campaign.failed_count += 1
                
            db.commit()
            
        print("\n--- Test Report Table ---")
        logs = db.query(MessageLog).filter(MessageLog.campaign_id == campaign_id).order_by(MessageLog.created_at.asc()).all()
        
        print(f"{'Recipient':<15} | {'Status':<15} | {'Retry':<5} | {'Delay(s)':<8} | {'Error'}")
        print("-" * 80)
        for log in logs:
            status = log.status
            delay = log.response_time if log.response_time is not None else 0
            err = status.replace('failed: ', '') if "failed" in status else "-"
            s = "Success" if log.status == "success" else "Failed"
            print(f"{log.recipient[:15]:<15} | {s:<15} | {log.retry_count:<5} | {delay:<8} | {err}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
