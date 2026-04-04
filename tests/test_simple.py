#!/usr/bin/env python3

"""
Simple tests without pytest dependency
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test all critical imports."""
    print("🧪 Testing Critical Imports...")
    
    try:
        # Test main application
        import main
        print("✅ Main application imported")
        
        # Test database
        from db.base import engine, Base
        from db.init_db import init_db
        print("✅ Database modules imported")
        
        # Test services
        from services import UserService, BusinessService
        print("✅ Services imported")
        
        # Test APIs
        from api.users import router as users_router
        from api.business import router as business_router
        print("✅ API routers imported")
        
        # Test schemas
        from schemas.user import LogoutResponseSchema
        from schemas.business import BusinessLogoutResponseSchema
        print("✅ Schemas imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_logout_endpoints():
    """Test logout endpoints exist."""
    print("\n🔍 Testing Logout Endpoints...")
    
    try:
        from api.users import router as users_router
        from api.business import router as business_router
        
        # Check user logout
        user_logout_found = False
        for route in users_router.routes:
            if 'logout' in route.path:
                user_logout_found = True
                print(f"✅ User logout endpoint: {list(route.methods)} {route.path}")
                break
        
        # Check business logout
        business_logout_found = False
        for route in business_router.routes:
            if 'logout' in route.path:
                business_logout_found = True
                print(f"✅ Business logout endpoint: {list(route.methods)} {route.path}")
                break
        
        if user_logout_found and business_logout_found:
            return True
        else:
            print("❌ Missing logout endpoints")
            return False
            
    except Exception as e:
        print(f"❌ Logout endpoint test failed: {e}")
        return False

def test_database_connection():
    """Test database connection."""
    print("\n🗄️  Testing Database Connection...")
    
    try:
        from db.base import engine
        from sqlalchemy import text
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run all simple tests."""
    print("🚀 Running Simple Tests (No Dependencies)")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Logout Endpoint Tests", test_logout_endpoints),
        ("Database Connection Tests", test_database_connection)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        if test_func():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
