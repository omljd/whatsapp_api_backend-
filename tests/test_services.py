#!/usr/bin/env python3

"""
Services tests
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_services_import():
    """Test all services import."""
    try:
        from services import (
            UserService,
            BusinessService,
            CreditDistributionService,
            MessageService,
            DeviceService,
            DeviceSessionService,
            MessageUsageService,
            OfficialWhatsAppConfigService,
            ResellerAnalyticsService
        )
        print("✅ All services import successfully")
    except Exception as e:
        pytest.fail(f"Services import failed: {e}")

def test_user_service_creation():
    """Test UserService creation."""
    try:
        from services.user_service import UserService
        from db.session import SessionLocal
        
        db = SessionLocal()
        user_service = UserService(db)
        assert user_service.db is not None
        db.close()
        print("✅ UserService creation successful")
    except Exception as e:
        pytest.fail(f"UserService creation failed: {e}")

def test_business_service_creation():
    """Test BusinessService creation."""
    try:
        from services.business_service import BusinessService
        from db.session import SessionLocal
        
        db = SessionLocal()
        business_service = BusinessService(db)
        assert business_service.db is not None
        db.close()
        print("✅ BusinessService creation successful")
    except Exception as e:
        pytest.fail(f"BusinessService creation failed: {e}")

def test_all_services_creation():
    """Test all services can be created."""
    try:
        from db.session import SessionLocal
        
        services = [
            ('user_service', 'UserService'),
            ('business_service', 'BusinessService'),
            ('credit_distribution_service', 'CreditDistributionService'),
            ('message_service', 'MessageService'),
            ('device_service', 'DeviceService'),
            ('device_session_service', 'DeviceSessionService'),
            ('message_usage_service', 'MessageUsageService'),
            ('official_whatsapp_config_service', 'OfficialWhatsAppConfigService'),
            ('reseller_analytics_service', 'ResellerAnalyticsService')
        ]
        
        db = SessionLocal()
        
        for module_name, class_name in services:
            module = __import__(f'services.{module_name}', fromlist=[class_name])
            service_class = getattr(module, class_name)
            service = service_class(db)
            assert service.db is not None
        
        db.close()
        print("✅ All services creation successful")
    except Exception as e:
        pytest.fail(f"Services creation test failed: {e}")

if __name__ == "__main__":
    test_services_import()
    test_user_service_creation()
    test_business_service_creation()
    test_all_services_creation()
    print("🎉 All services tests passed!")
