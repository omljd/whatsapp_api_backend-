from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional, Any
import uuid

from db.session import get_db
from api.auth import get_current_user
from services.busi_user_service import BusiUserService
from schemas.busi_user import (
    BusiUserProfileSchema,
    BusiUserProfileResponseSchema,
    BusiUserInfoSchema,
    BusiUserAddressSchema,
    BusiUserWalletSchema,
    BusiUserCreateSchema,
    BusiUserUpdateSchema,
    BusiUserResponseSchema,
    BusiUserLoginSchema,
    BusiUserResponseWithTokenSchema,
    BusiUserLogoutResponseSchema,
    BusiUserAnalyticsSchema,
    PlanResponseSchema,
)
from models.plan import Plan
from models.busi_user import BusiUser
from models.reseller import Reseller
from models.admin import MasterAdmin
from core.security import create_access_token, verify_token, create_refresh_token
from core.plan_validator import check_reseller_plan
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def map_busi_user_to_response(busi_user, db: Session = None) -> BusiUserResponseSchema:
    """Helper to map BusiUser ORM model to BusiUserResponseSchema with safe defaults."""
    try:
        connection_status = "disconnected"
        if db:
            from models.device import Device, SessionStatus
            is_connected = db.query(Device).filter(
                Device.busi_user_id == busi_user.busi_user_id,
                Device.session_status == SessionStatus.connected,
                Device.is_active == True
            ).first() is not None
            connection_status = "connected" if is_connected else "disconnected"

        response_data = {
            "busi_user_id": busi_user.busi_user_id,
            "role": busi_user.role or "business_owner",
            "status": busi_user.status or "active",
            "parent_reseller_id": busi_user.parent_reseller_id,
            "created_at": busi_user.created_at,
            "updated_at": busi_user.updated_at,
            "profile": {
                "name": busi_user.name or "",
                "username": busi_user.username or "",
                "email": busi_user.email or "",
                "phone": busi_user.phone or ""
            },
            "business": {
                "business_name": busi_user.business_name or "Unknown",
                "organization_type": getattr(busi_user, 'organization_type', None),
                "business_description": busi_user.business_description,
                "erp_system": busi_user.erp_system,
                "gstin": busi_user.gstin,
                "bank_name": getattr(busi_user, 'bank_name', None)
            },
            "address": {
                "full_address": busi_user.full_address,
                "pincode": busi_user.pincode,
                "country": busi_user.country
            } if busi_user.full_address else None,
            "wallet": {
                "credits_allocated": max(0, busi_user.credits_allocated or 0),
                "credits_used": max(0, busi_user.credits_used or 0),
                "credits_remaining": max(0, busi_user.credits_remaining or 0)
            },
            "whatsapp_mode": busi_user.whatsapp_mode or "unofficial",
            "plan_name": getattr(busi_user, 'plan_name', None),
            "plan_expiry": getattr(busi_user, 'plan_expiry', None),
            "connection_status": connection_status
        }
        return BusiUserResponseSchema(**response_data)
    except Exception as e:
        logger.error(f"Error mapping busi_user {getattr(busi_user, 'busi_user_id', 'unknown')}: {e}")
        raise e

router = APIRouter(tags=["busi_users"])


def get_busi_user_service(db: Session = Depends(get_db)) -> BusiUserService:
    return BusiUserService(db)


async def get_current_busi_user_id(authorization: str = Header(None)) -> uuid.UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload or payload.get("error"):
        error_type = payload.get("error", "invalid_token") if payload else "invalid_token"
        error_message = payload.get("message", "Invalid or expired token") if payload else "Invalid or expired token"
        
        if error_type == "token_expired":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message
            )
            
    if payload.get("type", "access") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Access token required."
        )

    # Check for business user roles (Admins allowed for management/debugging)
    role = (payload.get("role") or "").lower()
    if role not in ["user", "business_owner", "admin", "super_admin"]:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Business User or Admin only (role: {role})"
        )
    return uuid.UUID(payload.get("sub"))


async def get_current_reseller_token_id(authorization: str = Header(None)) -> uuid.UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload or payload.get("error"):
        error_type = payload.get("error", "invalid_token") if payload else "invalid_token"
        error_message = payload.get("message", "Invalid or expired token") if payload else "Invalid or expired token"
        
        if error_type == "token_expired":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message
            )
            
    if payload.get("type", "access") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Access token required."
        )

    # Check if role is reseller or admin
    role = (payload.get("role") or "").lower()
    if role not in ["reseller", "admin", "super_admin"]:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Reseller only (role: {role})"
        )
    return uuid.UUID(payload.get("sub"))


@router.get("/my-users", response_model=List[BusiUserResponseSchema])
async def get_my_busi_users(
    skip: int = 0,
    limit: int = 100,
    reseller_id: uuid.UUID = Depends(get_current_reseller_token_id),
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Get all business users belonging to the currently logged-in reseller."""
    busi_useres = busi_user_service.get_busi_useres_by_reseller(reseller_id, skip=skip, limit=limit)
    return [map_busi_user_to_response(bu, db=busi_user_service.db) for bu in busi_useres]


@router.get("/me", response_model=BusiUserResponseSchema)
async def get_current_busi_user(
    busi_user_id: uuid.UUID = Depends(get_current_busi_user_id),
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Get the profile of the currently logged-in business user."""
    busi_user = busi_user_service.get_busi_user_by_id(busi_user_id)
    if not busi_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BusiUser not found"
        )
    return map_busi_user_to_response(busi_user, db=busi_user_service.db)


@router.put("/me", response_model=BusiUserResponseSchema)
async def update_my_profile(
    busi_user_data: BusiUserUpdateSchema,
    busi_user_id: uuid.UUID = Depends(get_current_busi_user_id),
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Update the profile of the currently logged-in business user."""
    try:
        busi_user = busi_user_service.update_busi_user(busi_user_id, busi_user_data)
        if not busi_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BusiUser not found"
            )
        return map_busi_user_to_response(busi_user, db=busi_user_service.db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/analytics", response_model=BusiUserAnalyticsSchema)
async def get_busi_user_analytics(
    reseller_id: uuid.UUID = Depends(get_current_reseller_token_id),
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Get analytics for the logged-in reseller's business users."""
    stats = busi_user_service.get_reseller_analytics(reseller_id)
    return BusiUserAnalyticsSchema(**stats)


@router.post("/register", response_model=BusiUserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_busi_user(
    busi_user_data: BusiUserCreateSchema, 
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Register a new busi_user user."""
    # NEW: Check if the reseller in the data is actually a reseller and what is their plan status
    # This assumes signups are done by resellers. If it's a public signup, logic might differ.
    if busi_user_data.parent_reseller_id:
        check_reseller_plan(busi_user_service.db, uuid.UUID(str(busi_user_data.parent_reseller_id)))
    
    try:
        created_by = None
        if busi_user_data.parent_reseller_id:
            created_by = busi_user_data.parent_reseller_id
        
        busi_user = busi_user_service.create_busi_user(busi_user_data, created_by=created_by)
        
        return map_busi_user_to_response(busi_user, db=busi_user_service.db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating busi_user: {str(e)}"
        )


@router.post("/login", response_model=BusiUserResponseWithTokenSchema)
async def login_busi_user(
    login_data: BusiUserLoginSchema,
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Authenticate busi_user and return access token."""
    busi_user = busi_user_service.authenticate_busi_user(login_data.email, login_data.password)
    if not busi_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if busi_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )

    access_token = create_access_token(
        data={"sub": str(busi_user.busi_user_id), "email": busi_user.email, "role": busi_user.role}
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(busi_user.busi_user_id), "email": busi_user.email, "role": busi_user.role}
    )

    return BusiUserResponseWithTokenSchema(
        busi_user=map_busi_user_to_response(busi_user, db=busi_user_service.db),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/", response_model=List[BusiUserResponseSchema])
async def get_busi_useres(
    skip: int = 0,
    limit: int = 100,
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Get all busi_useres with pagination."""
    busi_useres = busi_user_service.get_all_busi_useres(skip=skip, limit=limit)
    return [map_busi_user_to_response(bu, db=busi_user_service.db) for bu in busi_useres]


@router.get("/reseller/{reseller_id}", response_model=List[BusiUserResponseSchema])
async def get_busi_useres_by_reseller(
    reseller_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Get all busi_useres under a specific reseller."""
    busi_useres = busi_user_service.get_busi_useres_by_reseller(reseller_id, skip=skip, limit=limit)
    return [map_busi_user_to_response(bu, db=busi_user_service.db) for bu in busi_useres]


@router.post("/logout", response_model=BusiUserLogoutResponseSchema)
async def logout_busi_user():
    """Logout busi_user user."""
    return BusiUserLogoutResponseSchema(
        message="BusiUser successfully logged out",
        detail="BusiUser session terminated, please discard your access token"
    )


@router.get("/plans/available", response_model=List[PlanResponseSchema])
async def get_available_plans(
    db: Session = Depends(get_db)
):
    """Get all available plans for business users."""
    plans = db.query(Plan).filter(Plan.plan_category == "BUSINESS", Plan.status == "active").all()
    return plans


@router.get("/me/plan", response_model=dict)
async def get_my_plan(
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current plan of the logged-in user (Business User, Reseller, or Admin).
    Now standardized to prevent 403 errors across roles.
    """
    # 1. Handle Business Users
    if isinstance(current_user, BusiUser):
        # Fetch assigner name
        assigned_by_name = "Administrator"
        assigned_by_role = "admin"
        if current_user.parent_reseller_id:
            from models.reseller import Reseller
            reseller = db.query(Reseller).filter(Reseller.reseller_id == current_user.parent_reseller_id).first()
            if reseller:
                assigned_by_name = reseller.name
                assigned_by_role = "reseller"

        # Auto-heal missing plan relationship
        user_plan = current_user.plan
        if not user_plan and getattr(current_user, 'plan_name', None):
            from models.plan import Plan
            fetched_plan = db.query(Plan).filter(Plan.name == current_user.plan_name).first()
            if fetched_plan:
                current_user.plan_id = fetched_plan.plan_id
                db.commit()
                user_plan = fetched_plan

        return {
            "user_type": "business",
            "plan_id": str(current_user.plan_id) if current_user.plan_id else None,
            "plan_name": current_user.plan_name or (user_plan.name if user_plan else "No Active Plan"),
            "plan_expiry": current_user.plan_expiry.isoformat() if current_user.plan_expiry else None,
            "credits_remaining": current_user.credits_remaining or 0,
            "credits_allocated": current_user.credits_allocated or (user_plan.credits_offered if user_plan else 0),
            "credits_used": current_user.credits_used or 0,
            "whatsapp_mode": current_user.whatsapp_mode or "unofficial",
            "assigned_by_name": assigned_by_name,
            "assigned_by_role": assigned_by_role,
            "is_active": True if user_plan else False,
            "plan": PlanResponseSchema.model_validate(user_plan).model_dump() if user_plan else None
        }
    
    # 2. Handle Resellers
    elif isinstance(current_user, Reseller):
        return {
            "user_type": "reseller",
            "plan_id": str(current_user.plan_id) if current_user.plan_id else None,
            "plan_name": current_user.plan_name or (current_user.plan.name if current_user.plan else "Reseller Portal"),
            "plan_expiry": current_user.plan_expiry.isoformat() if current_user.plan_expiry else None,
            "credits_remaining": current_user.available_credits or 0,
            "credits_allocated": current_user.total_credits or (current_user.plan.credits_offered if current_user.plan else 0),
            "credits_used": current_user.used_credits or 0,
            "whatsapp_mode": "reseller_portal",
            "assigned_by_name": "System",
            "assigned_by_role": "admin",
            "is_active": True if current_user.plan_id else False,
            "plan": PlanResponseSchema.model_validate(current_user.plan).model_dump() if current_user.plan else None
        }
    
    # 3. Handle System Administrators
    elif isinstance(current_user, MasterAdmin):
        return {
            "user_type": "admin",
            "plan_id": "admin-unlimited",
            "plan_name": "System Administrator",
            "plan_expiry": None,
            "credits_remaining": 999999,
            "credits_allocated": 999999,
            "credits_used": 0,
            "whatsapp_mode": "admin",
            "plan": {
                "name": "Super Admin Plan",
                "price": 0,
                "credits_offered": 999999,
                "validity_days": 365,
                "plan_category": "ADMIN"
            }
        }
    
    else:
        raise HTTPException(status_code=403, detail="Invalid user role for plan retrieval")


@router.get("/{busi_user_id}", response_model=BusiUserResponseSchema)
async def get_busi_user(
    busi_user_id: uuid.UUID,
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Get a specific busi_user by ID."""
    busi_user = busi_user_service.get_busi_user_by_id(busi_user_id)
    if not busi_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BusiUser not found"
        )
    
    return map_busi_user_to_response(busi_user, db=busi_user_service.db)


@router.put("/{busi_user_id}", response_model=BusiUserResponseSchema)
async def update_busi_user(
    busi_user_id: uuid.UUID,
    busi_user_data: BusiUserUpdateSchema,
    reseller_id: uuid.UUID = Depends(get_current_reseller_token_id),
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Update a specific busi_user."""
    # NEW: Check Reseller Plan/Credits before updating user (e.g. allocating credits)
    check_reseller_plan(busi_user_service.db, reseller_id)

    try:
        busi_user = busi_user_service.update_busi_user(busi_user_id, busi_user_data, reseller_id)
        if not busi_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BusiUser not found"
            )
        
        return map_busi_user_to_response(busi_user, db=busi_user_service.db)
    except ValueError as e:
        status_code = status.HTTP_400_BAD_REQUEST
        if "Unauthorized" in str(e):
             status_code = status.HTTP_403_FORBIDDEN
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )


@router.delete("/{busi_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_busi_user(
    busi_user_id: uuid.UUID,
    reseller_id: uuid.UUID = Depends(get_current_reseller_token_id),
    busi_user_service: BusiUserService = Depends(get_busi_user_service)
):
    """Delete a specific busi_user."""
    try:
        success = busi_user_service.delete_busi_user(busi_user_id, reseller_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BusiUser not found"
            )
    except ValueError as e:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )



