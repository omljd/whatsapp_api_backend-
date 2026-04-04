from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.busi_user import BusiUser
from models.reseller import Reseller
import uuid

def check_busi_user_plan(db: Session, busi_user_id: str):
    """
    Checks if a business user has a valid plan and remaining credits.
    Raises HTTPException if not.
    """
    user = db.query(BusiUser).filter(BusiUser.busi_user_id == busi_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business user not found"
        )
    
    # 1. Check Plan Expiry
    if not user.plan_expiry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active plan found. Please purchase a plan to continue."
        )
    
    # Robust comparison: Ensure both are aware or both are naive
    now = datetime.now(timezone.utc)
    plan_expiry = user.plan_expiry
    if plan_expiry.tzinfo is None:
        plan_expiry = plan_expiry.replace(tzinfo=timezone.utc)

    if plan_expiry < now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your plan has expired. Please renew your plan to continue."
        )
    
    # 2. Check Credits
    if (user.credits_remaining or 0) <= 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient credits. Please recharge your wallet to continue."
        )
    
    return user

def check_reseller_plan(db: Session, reseller_id: str):
    """
    Checks if a reseller has a valid plan and remaining credits.
    Raises HTTPException if not.
    """
    reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
    if not reseller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reseller not found"
        )
    
    # 1. Check Plan Expiry
    if not reseller.plan_expiry:
         # Resellers might not have a "plan" in the same way, but they need credits
         pass
    else:
        now = datetime.now(timezone.utc)
        plan_expiry = reseller.plan_expiry
        if plan_expiry.tzinfo is None:
            plan_expiry = plan_expiry.replace(tzinfo=timezone.utc)

        if plan_expiry < now:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your reseller plan has expired. Please contact admin."
            )
    
    # 2. Check Credits (Available credits for allocation)
    if (reseller.available_credits or 0) <= 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient credits in reseller wallet. Please purchase more credits to allocate."
        )
    
    return reseller
