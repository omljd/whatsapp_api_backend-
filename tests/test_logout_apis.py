#!/usr/bin/env python3

"""
Logout API tests
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_user_logout_api_import():
    """Test user logout API import."""
    try:
        from api.users import router as users_router
        from schemas.user import LogoutResponseSchema
        
        # Check if logout endpoint exists
        logout_routes = [route for route in users_router.routes if 'logout' in route.path]
        assert len(logout_routes) > 0, "User logout endpoint not found"
        
        # Check response schema
        schema_fields = LogoutResponseSchema.__fields__
        assert 'message' in schema_fields
        assert 'detail' in schema_fields
        
        print("✅ User logout API import successful")
    except Exception as e:
        pytest.fail(f"User logout API import failed: {e}")

def test_business_logout_api_import():
    """Test business logout API import."""
    try:
        from api.business import router as business_router
        from schemas.business import BusinessLogoutResponseSchema
        
        # Check if logout endpoint exists
        logout_routes = [route for route in business_router.routes if 'logout' in route.path]
        assert len(logout_routes) > 0, "Business logout endpoint not found"
        
        # Check response schema
        schema_fields = BusinessLogoutResponseSchema.__fields__
        assert 'message' in schema_fields
        assert 'detail' in schema_fields
        assert 'business_type' in schema_fields
        
        print("✅ Business logout API import successful")
    except Exception as e:
        pytest.fail(f"Business logout API import failed: {e}")

def test_logout_endpoints_structure():
    """Test logout endpoints structure."""
    try:
        from api.users import router as users_router
        from api.business import router as business_router
        
        # Test user logout endpoint
        user_logout = None
        for route in users_router.routes:
            if 'logout' in route.path:
                user_logout = route
                break
        
        assert user_logout is not None, "User logout endpoint not found"
        assert 'POST' in user_logout.methods, "User logout should support POST"
        
        # Test business logout endpoint
        business_logout = None
        for route in business_router.routes:
            if 'logout' in route.path:
                business_logout = route
                break
        
        assert business_logout is not None, "Business logout endpoint not found"
        assert 'POST' in business_logout.methods, "Business logout should support POST"
        
        print("✅ Logout endpoints structure correct")
    except Exception as e:
        pytest.fail(f"Logout endpoints structure test failed: {e}")

def test_logout_response_schemas():
    """Test logout response schemas."""
    try:
        from schemas.user import LogoutResponseSchema
        from schemas.business import BusinessLogoutResponseSchema
        
        # Test user logout schema
        user_response = LogoutResponseSchema(
            message="Successfully logged out",
            detail="Please discard your access token"
        )
        assert user_response.message == "Successfully logged out"
        assert user_response.detail == "Please discard your access token"
        
        # Test business logout schema
        business_response = BusinessLogoutResponseSchema(
            message="Business successfully logged out",
            detail="Business session terminated",
            business_type="business"
        )
        assert business_response.message == "Business successfully logged out"
        assert business_response.detail == "Business session terminated"
        assert business_response.business_type == "business"
        
        print("✅ Logout response schemas working")
    except Exception as e:
        pytest.fail(f"Logout response schemas test failed: {e}")

if __name__ == "__main__":
    test_user_logout_api_import()
    test_business_logout_api_import()
    test_logout_endpoints_structure()
    test_logout_response_schemas()
    print("🎉 All logout API tests passed!")
