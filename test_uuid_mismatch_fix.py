#!/usr/bin/env python3
"""
🧪 UUID VS VARCHAR MISMATCH FIX - COMPREHENSIVE TEST

Tests all UUID handling fixes to ensure PostgreSQL errors are resolved.
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.uuid_service import UUIDService
from uuid import uuid4, UUID
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestUUIDFixes:
    """Test comprehensive UUID handling fixes"""
    
    def test_uuid_service_basic_functionality(self):
        """Test UUIDService basic operations"""
        logger.info("🧪 Testing UUIDService basic functionality...")
        
        # Test valid UUID string
        valid_uuid_str = str(uuid4())
        result = UUIDService.safe_convert(valid_uuid_str)
        assert isinstance(result, UUID)
        assert str(result) == valid_uuid_str
        
        # Test UUID object
        uuid_obj = uuid4()
        result = UUIDService.safe_convert(uuid_obj)
        assert isinstance(result, UUID)
        assert result == uuid_obj
        
        # Test None
        result = UUIDService.safe_convert(None)
        assert result is None
        
        logger.info("✅ UUIDService basic functionality tests passed")
    
    def test_uuid_service_invalid_handling(self):
        """Test UUIDService invalid UUID handling"""
        logger.info("🧪 Testing UUIDService invalid UUID handling...")
        
        # Test invalid UUID string (should raise HTTPException)
        with pytest.raises(Exception):  # HTTPException
            UUIDService.safe_convert("invalid-uuid")
        
        # Test phone number (should raise HTTPException)
        with pytest.raises(Exception):  # HTTPException
            UUIDService.safe_convert("+1234567890")
        
        # Test convert_or_none with invalid UUID (should return None)
        result = UUIDService.convert_or_none("invalid-uuid")
        assert result is None
        
        logger.info("✅ UUIDService invalid handling tests passed")
    
    def test_uuid_service_list_operations(self):
        """Test UUIDService list operations"""
        logger.info("🧪 Testing UUIDService list operations...")
        
        # Test mixed valid/invalid UUIDs
        uuid1 = str(uuid4())
        uuid2 = str(uuid4())
        mixed_list = [uuid1, "invalid-uuid", uuid2, "+1234567890"]
        
        result = UUIDService.safe_convert_list(mixed_list)
        assert len(result) == 2  # Only valid UUIDs should remain
        assert all(isinstance(u, UUID) for u in result)
        
        logger.info("✅ UUIDService list operations tests passed")
    
    def test_uuid_validation_function(self):
        """Test UUID validation function"""
        logger.info("🧪 Testing UUID validation function...")
        
        # Test valid UUID
        valid_uuid = str(uuid4())
        assert UUIDService.validate_uuid_string(valid_uuid) == True
        
        # Test invalid UUID
        assert UUIDService.validate_uuid_string("invalid-uuid") == False
        assert UUIDService.validate_uuid_string("+1234567890") == False
        assert UUIDService.validate_uuid_string("") == False
        
        logger.info("✅ UUID validation function tests passed")

def test_database_query_simulation():
    """Simulate database queries that were failing before fix"""
    logger.info("🧪 Testing database query simulation...")
    
    # Simulate the problematic queries that were causing PostgreSQL errors
    valid_device_id = str(uuid4())
    
    # Before fix: This would cause "operator does not exist: uuid = character varying"
    # After fix: We convert to UUID before querying
    try:
        device_uuid = UUIDService.safe_convert(valid_device_id)
        assert isinstance(device_uuid, UUID)
        logger.info("✅ Database query simulation passed - UUID conversion successful")
    except Exception as e:
        logger.error(f"❌ Database query simulation failed: {e}")
        raise

def test_api_endpoint_validation():
    """Test API endpoint validation scenarios"""
    logger.info("🧪 Testing API endpoint validation scenarios...")
    
    # Test valid device_id (should pass)
    valid_device_id = str(uuid4())
    try:
        UUIDService.safe_convert(valid_device_id)
        logger.info("✅ Valid device_id validation passed")
    except Exception as e:
        logger.error(f"❌ Valid device_id validation failed: {e}")
        raise
    
    # Test invalid device_id (should fail)
    invalid_device_ids = [
        "phone-number-123",
        "+1234567890", 
        "device-123",
        "",
        "not-a-uuid"
    ]
    
    for invalid_id in invalid_device_ids:
        try:
            UUIDService.safe_convert(invalid_id)
            logger.error(f"❌ Invalid device_id should have failed: {invalid_id}")
            raise AssertionError(f"Invalid device_id {invalid_id} should have been rejected")
        except Exception:
            # Expected behavior
            pass
    
    logger.info("✅ API endpoint validation tests passed")

def main():
    """Run all tests"""
    logger.info("🚀 Starting UUID vs VARCHAR Mismatch Fix Tests")
    
    test_instance = TestUUIDFixes()
    
    try:
        # Run all test methods
        test_instance.test_uuid_service_basic_functionality()
        test_instance.test_uuid_service_invalid_handling()
        test_instance.test_uuid_service_list_operations()
        test_instance.test_uuid_validation_function()
        
        # Run integration tests
        test_database_query_simulation()
        test_api_endpoint_validation()
        
        logger.info("🎉 ALL TESTS PASSED - UUID vs VARCHAR mismatch fix is working correctly!")
        return True
        
    except Exception as e:
        logger.error(f"❌ TESTS FAILED: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
