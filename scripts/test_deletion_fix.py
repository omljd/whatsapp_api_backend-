import sys
import os
import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timezone

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from db.session import SessionLocal
from models.busi_user import BusiUser
from models.google_sheet import GoogleSheet, SheetStatus
from models.campaign import Campaign, CampaignStatus

def test_deletion():
    db = SessionLocal()
    try:
        print("🛠️ Setting up test data...")
        
        # 1. Create a dummy user
        user_id = uuid.uuid4()
        user = BusiUser(
            busi_user_id=user_id,
            name="Test User",
            username=f"testuser_{uuid.uuid4().hex[:6]}",
            email=f"test_{uuid.uuid4().hex[:6]}@example.com",
            phone=f"{uuid.uuid4().int % 10**10}",
            password_hash="dummy",
            business_name="Test Business"
        )
        db.add(user)
        db.flush() # Sync ID
        
        # 2. Create a dummy google sheet
        sheet_id = uuid.uuid4()
        sheet = GoogleSheet(
            id=sheet_id,
            user_id=user_id,
            sheet_name="Test Sheet",
            spreadsheet_id="dummy_spreadsheet_id",
            status=SheetStatus.ACTIVE
        )
        db.add(sheet)
        db.flush()
        
        # 3. Create a dummy campaign
        campaign_id = uuid.uuid4()
        campaign = Campaign(
            id=campaign_id,
            busi_user_id=user_id,
            sheet_id=sheet_id,
            name="Test Campaign",
            status=CampaignStatus.PENDING
        )
        db.add(campaign)
        db.commit()
        print(f"✅ Test data created. User: {user_id}, Sheet: {sheet_id}, Campaign: {campaign_id}")
        
        # 4. Attempt to delete the user
        print("🗑️ Attempting to delete user...")
        user_to_delete = db.query(BusiUser).filter(BusiUser.busi_user_id == user_id).first()
        if not user_to_delete:
            print("❌ Error: User not found before deletion")
            return
            
        db.delete(user_to_delete)
        db.commit()
        print("✅ User deleted successfully!")
        
        # 5. Verify cleanup
        print("🔍 Verifying cleanup...")
        rem_user = db.query(BusiUser).filter(BusiUser.busi_user_id == user_id).first()
        rem_sheet = db.query(GoogleSheet).filter(GoogleSheet.id == sheet_id).first()
        rem_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if rem_user or rem_sheet or rem_campaign:
            print(f"❌ Cleanup failed! Remaining: User={bool(rem_user)}, Sheet={bool(rem_sheet)}, Campaign={bool(rem_campaign)}")
        else:
            print("✅ All related records were successfully deleted.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Deletion test failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_deletion()
