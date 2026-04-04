import sys
sys.path.append('.')
from db.session import SessionLocal
from models.busi_user import BusiUser
from models.reseller import Reseller
from services.credit_distribution_service import CreditDistributionService
from schemas.credit_distribution import CreditDistributionCreateSchema
from datetime import datetime
import uuid

db = SessionLocal()

print("=== Testing Credit Distribution ===")

# Get business user and reseller
business_user = db.query(BusiUser).filter(BusiUser.busi_user_id == 'a4ea62f8-b476-4c80-810b-f8f681029944').first()
reseller = db.query(Reseller).filter(Reseller.reseller_id == business_user.parent_reseller_id).first()

if business_user and reseller:
    print(f"Business User: {business_user.business_name} - {business_user.credits_remaining} credits")
    print(f"Parent Reseller: {reseller.name} - {reseller.available_credits} credits")
    
    # Test credit distribution
    try:
        distribution_data = CreditDistributionCreateSchema(
            from_reseller_id=reseller.reseller_id,
            to_business_user_id=str(business_user.busi_user_id),
            credits_shared=1000,
            notes="Test credit distribution"
        )
        
        service = CreditDistributionService(db)
        distribution = service.distribute_credits(distribution_data, reseller.reseller_id)
        
        print(f"✅ Successfully distributed {distribution_data.credits_shared} credits")
        print(f"Distribution ID: {distribution.distribution_id}")
        
        # Check updated balances
        db.refresh(business_user)
        db.refresh(reseller)
        print(f"Business user new balance: {business_user.credits_remaining}")
        print(f"Reseller new available credits: {reseller.available_credits}")
        
    except Exception as e:
        print(f"❌ Distribution failed: {e}")

else:
    print("❌ Business user or reseller not found")

db.close()
