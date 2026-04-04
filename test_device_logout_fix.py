#!/usr/bin/env python3
"""
Test script to verify device logout fixes
"""

import logging
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment or .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        import os
        return os.getenv("DATABASE_URL")
    except ImportError:
        logger.error("python-dotenv not installed")
        return None

def test_database_schema():
    """Test that all required columns exist"""
    logger.info("🔍 Testing database schema...")
    
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ DATABASE_URL not found")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Test google_sheet_triggers columns
            required_columns = [
                "last_processed_row",
                "phone_column", 
                "status_column",
                "trigger_value",
                "message_template"
            ]
            
            for column in required_columns:
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'google_sheet_triggers' 
                    AND column_name = :column_name
                """), {"column_name": column})
                
                if result.fetchone():
                    logger.info(f"✅ Column {column} exists")
                else:
                    logger.error(f"❌ Column {column} missing")
                    return False
            
            logger.info("✅ All required columns exist in google_sheet_triggers")
            return True
            
    except Exception as e:
        logger.error(f"❌ Schema test failed: {e}")
        return False

def test_model_imports():
    """Test that model imports work correctly"""
    logger.info("🔍 Testing model imports...")
    
    try:
        from models.google_sheet import GoogleSheetTrigger
        from models.device import Device, SessionStatus
        from schemas.device import SessionStatus as SchemaSessionStatus
        
        # Test enum values match
        model_statuses = {status.value for status in SessionStatus}
        schema_statuses = {status.value for status in SchemaSessionStatus}
        
        if model_statuses == schema_statuses:
            logger.info("✅ Model and schema SessionStatus enums match")
            logger.info(f"✅ Available statuses: {sorted(model_statuses)}")
            return True
        else:
            logger.error(f"❌ Status mismatch - Model: {model_statuses}, Schema: {schema_statuses}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Import test failed: {e}")
        return False

def test_device_logout_flow():
    """Test device logout flow with a mock device"""
    logger.info("🔍 Testing device logout flow...")
    
    try:
        from services.device_service import DeviceService
        from models.device import SessionStatus
        
        database_url = get_database_url()
        if not database_url:
            return False
            
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            device_service = DeviceService(db)
            
            # Test logout with non-existent device (should return device_not_found)
            result = device_service.logout_device("00000000-0000-0000-0000-000000000000")
            
            if not result["success"] and result.get("error") == "device_not_found":
                logger.info("✅ Non-existent device handled correctly")
            else:
                logger.error(f"❌ Unexpected result for non-existent device: {result}")
                return False
                
            logger.info("✅ Device logout flow test passed")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Logout flow test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting device logout fix verification...")
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Model Imports", test_model_imports),
        ("Device Logout Flow", test_device_logout_flow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        if test_func():
            logger.info(f"✅ {test_name} test PASSED")
            passed += 1
        else:
            logger.error(f"❌ {test_name} test FAILED")
    
    logger.info(f"\n--- Test Results ---")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! Device logout fixes are working correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
