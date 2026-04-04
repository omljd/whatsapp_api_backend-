import sys
import os
sys.path.append(r"d:\master admin dashboard 2 integration 30-3-2026\whatsapp-api-backend")

from db.session import SessionLocal
from models.busi_user import BusiUser
from models.campaign import Campaign
from models.device import Device, DeviceType
from models.google_sheet import GoogleSheet
import uuid
from api.admin import delete_platform_user
from fastapi import HTTPException
from unittest.mock import MagicMock
import asyncio

async def test_full_cascade():
    db = SessionLocal()
    try:
        # 1. Create Dummy User
        dummy_id = uuid.uuid4()
        user = BusiUser(
            busi_user_id=dummy_id,
            name="Deletion Test User",
            email=f"test_del_{uuid.uuid4().hex[:8]}@example.com",
            username=f"test_del_{uuid.uuid4().hex[:8]}",
            phone=f"12345{uuid.uuid4().hex[:5]}",
            password_hash="fake_hash",
            business_name="Test Corp"
        )
        db.add(user)
        
        # 2. Add Dummy Data
        sheet = GoogleSheet(id=uuid.uuid4(), user_id=dummy_id, sheet_name="Test Sheet", spreadsheet_id="fake_id")
        db.add(sheet)
        
        device = Device(device_id=uuid.uuid4(), busi_user_id=dummy_id, device_name="Test Phone", device_type=DeviceType.web)
        db.add(device)
        
        campaign = Campaign(id=uuid.uuid4(), busi_user_id=dummy_id, sheet_id=sheet.id, name="Test Campaign")
        db.add(campaign)
        
        db.commit()
        print(f"Created dummy user {dummy_id} with data.")
        
        # 3. Call the delete function
        # Mocking current_admin
        mock_admin = MagicMock()
        mock_admin.admin_id = uuid.uuid4()
        
        from models.admin import MasterAdmin
        # We need an actual MasterAdmin instance if isinstance check is used
        real_mock_admin = MasterAdmin(admin_id=uuid.uuid4())
        
        print("Executing delete_platform_user...")
        result = await delete_platform_user(dummy_id, db, real_mock_admin)
        print(f"Result: {result}")
        
        # 4. Verify
        exists = db.query(BusiUser).filter(BusiUser.busi_user_id == dummy_id).first()
        if not exists:
            print("✅ User deleted successfully.")
        else:
            print("❌ User still exists.")
            
        # Verify related
        sheets = db.query(GoogleSheet).filter(GoogleSheet.user_id == dummy_id).count()
        print(f"Remaining sheets: {sheets}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_full_cascade())
