import sys
import os
import asyncio
from uuid import UUID
import uuid

# Add current directory to path
sys.path.append(os.getcwd())

from db.session import SessionLocal
from models.reseller import Reseller
from models.busi_user import BusiUser
from models.audit_log import AuditLog
from models.reseller_analytics import ResellerAnalytics
from models.credit_distribution import CreditDistribution
from models.plan import Plan
from api.admin import delete_platform_user

async def test_reseller_deletion():
    db = SessionLocal()
    test_id = str(uuid.uuid4())[:8]
    username = f"test_reseller_{test_id}"
    email = f"test_reseller_{test_id}@example.com"
    managed_username = f"managed_user_{test_id}"
    managed_email = f"managed_user_{test_id}@example.com"
    
    print(f"🚀 Starting verification for reseller deletion fix...")
    
    try:
        # 1. Create a test reseller
        reseller = Reseller(
            name="Test Reseller",
            username=username,
            email=email,
            phone=f"123456{test_id}",
            password_hash="fakehash",
            role="reseller",
            available_credits=100
        )
        db.add(reseller)
        db.commit()
        db.refresh(reseller)
        reseller_id = reseller.reseller_id
        print(f"✅ Created reseller: {reseller_id} ({username})")
        
        # 2. Create related records
        # Audit Log
        audit_log = AuditLog(
            reseller_id=reseller_id,
            performed_by_id=reseller_id,
            performed_by_name="Test Reseller",
            performed_by_role="reseller",
            action_type="TEST ACTION",
            module="TEST",
            description="Initial test log"
        )
        db.add(audit_log)
        
        # Reseller Analytics
        analytics = ResellerAnalytics(
            reseller_id=reseller_id,
            total_credits_purchased=100,
            remaining_credits=100
        )
        db.add(analytics)
        
        # Managed User
        managed_user = BusiUser(
            name="Managed User",
            username=managed_username,
            email=managed_email,
            phone=f"987654{test_id}",
            password_hash="fakehash",
            business_name="Test Business",
            parent_reseller_id=reseller_id,
            parent_role="reseller"
        )
        db.add(managed_user)
        
        # Credit Distribution
        dist = CreditDistribution(
            from_reseller_id=reseller_id,
            to_business_user_id=uuid.uuid4(), # Just a dummy ID for FK, wait BusiUser needs to exist
            credits_shared=10
        )
        # Re-using managed_user_id for distribution
        db.flush() # To get managed_user.busi_user_id
        dist.to_business_user_id = managed_user.busi_user_id
        db.add(dist)
        
        db.commit()
        print("✅ Created related records (AuditLog, Analytics, Managed User, CreditDistribution)")
        
        # 3. Call the delete function
        print(f"🔄 Attempting to delete reseller {reseller_id}...")
        # Note: delete_platform_user is an async function in api/admin.py
        result = await delete_platform_user(reseller_id, db)
        print(f"📊 Delete result: {result}")
        
        # 4. Verify cleanup
        # Reseller should be gone
        reseller_check = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        print(f"🧐 Reseller still exists in DB? {'Yes ❌' if reseller_check else 'No ✅'}")
        
        # Audit log should have NULL reseller_id
        log_check = db.query(AuditLog).filter(AuditLog.performed_by_id == reseller_id).first()
        print(f"🧐 Audit log reseller_id nullified? {'Yes ✅' if log_check and log_check.reseller_id is None else 'No ❌'}")
        
        # Analytics should be gone
        analytics_check = db.query(ResellerAnalytics).filter(ResellerAnalytics.reseller_id == reseller_id).first()
        print(f"🧐 Reseller Analytics deleted? {'No ❌' if analytics_check else 'Yes ✅'}")
        
        # Credit Partition should be gone
        dist_check = db.query(CreditDistribution).filter(CreditDistribution.from_reseller_id == reseller_id).first()
        print(f"🧐 Credit Distribution deleted? {'No ❌' if dist_check else 'Yes ✅'}")
        
        # Managed user should be promoted
        user_check = db.query(BusiUser).filter(BusiUser.username == managed_username).first()
        is_promoted = user_check and user_check.parent_reseller_id is None and user_check.parent_role == "admin"
        print(f"🧐 Managed user promoted to Admin? {'Yes ✅' if is_promoted else 'No ❌'}")
        
        if not reseller_check and log_check and log_check.reseller_id is None and not analytics_check and not dist_check and is_promoted:
            print("\n🎉 ALL TESTS PASSED: Reseller deleted successfully without ForeignKeyViolation!")
        else:
            print("\n⚠️ SOME TESTS FAILED: Please check the output above.")
            
    except Exception as e:
        print(f"\n❌ ERROR during verification: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        # Cleanup remaining test data
        print("\n🧹 Cleaning up test data...")
        try:
            db.query(AuditLog).filter(AuditLog.performed_by_id == reseller_id).delete()
            db.query(BusiUser).filter(BusiUser.username == managed_username).delete()
            db.query(Reseller).filter(Reseller.username == username).delete()
            db.commit()
        except Exception as cleanup_err:
            print(f"Cleanup error: {cleanup_err}")
            db.rollback()
        db.close()

if __name__ == "__main__":
    asyncio.run(test_reseller_deletion())
