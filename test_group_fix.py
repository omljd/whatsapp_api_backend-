#!/usr/bin/env python3
"""
Test script to verify group creation and contact addition fixes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from db.session import SessionLocal
from services.group_service import GroupService
from models.contact_group import ContactGroup
from models.busi_user import BusiUser
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_group_persistence():
    """Test that groups persist correctly in DB"""
    
    # Create a test database session
    db = SessionLocal()
    
    try:
        # Find a test user
        test_user = db.query(BusiUser).first()
        if not test_user:
            logger.error("No test user found in database")
            return False
            
        logger.info(f"Using test user: {test_user.busi_user_id}")
        
        # Test group creation
        group_service = GroupService(db)
        
        # Create a test group
        test_group_name = f"test_group_{uuid.uuid4().hex[:8]}"
        logger.info(f"Creating test group: {test_group_name}")
        
        group = group_service.create_group(
            user_id=test_user.busi_user_id,
            name=test_group_name,
            description="Test group for persistence verification"
        )
        
        logger.info(f"Group created with ID: {group.group_id}")
        
        # Verify group exists immediately after creation
        verification_check = db.query(ContactGroup).filter(
            ContactGroup.group_id == group.group_id
        ).first()
        
        if verification_check:
            logger.info("✅ GROUP PERSISTENCE VERIFICATION: Group exists in DB immediately after creation")
        else:
            logger.error("❌ GROUP PERSISTENCE FAILED: Group not found in DB after creation")
            return False
            
        # Test adding contacts to the group
        contact_data = [
            {"name": "Test Contact 1", "phone": "+12345678901"},
            {"name": "Test Contact 2", "phone": "+12345678902"}
        ]
        
        logger.info("Adding test contacts to group...")
        result = group_service.add_contacts_to_group(
            group_id=group.group_id,
            user_id=test_user.busi_user_id,
            contact_data=contact_data
        )
        
        logger.info(f"Contacts addition result: {result}")
        
        if result.get("success"):
            logger.info("✅ CONTACT ADDITION SUCCESS: No FK violation")
        else:
            logger.error("❌ CONTACT ADDITION FAILED")
            return False
            
        # Clean up - delete test group
        group_service.delete_group(group.group_id, test_user.busi_user_id)
        logger.info("Test group cleaned up")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting group persistence test...")
    success = test_group_persistence()
    
    if success:
        logger.info("🎉 ALL TESTS PASSED: Group persistence fix is working correctly!")
    else:
        logger.error("💥 TESTS FAILED: Issues remain with group persistence")
        
    sys.exit(0 if success else 1)
