#!/usr/bin/env python3

"""
Main application tests
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_main_import():
    """Test that main application imports successfully."""
    try:
        import main
        assert main.app is not None
        print("✅ Main application imports successfully")
    except Exception as e:
        pytest.fail(f"Main import failed: {e}")

def test_app_creation():
    """Test FastAPI app creation."""
    try:
        import main
        app = main.app
        assert app.title == "WhatsApp Platform Backend"
        assert app.version == "1.0.0"
        print("✅ FastAPI app created successfully")
    except Exception as e:
        pytest.fail(f"App creation failed: {e}")

def test_router_inclusion():
    """Test that all routers are included."""
    try:
        import main
        app = main.app
        
        # Check if routes exist
        routes = [route.path for route in app.routes]
        
        expected_routes = [
            "/docs",
            "/redoc", 
            "/api/users",
            "/api/businesses",
            "/api/credit-distributions",
            "/api/messages",
            "/api/devices",
            "/api/device-sessions",
            "/api/message-usage",
            "/api/reseller-analytics",
            "/api/official-whatsapp-config"
        ]
        
        for route in expected_routes:
            assert any(route in r for r in routes), f"Route {route} not found"
        
        print("✅ All routers included successfully")
    except Exception as e:
        pytest.fail(f"Router inclusion test failed: {e}")

if __name__ == "__main__":
    test_main_import()
    test_app_creation()
    test_router_inclusion()
    print("🎉 All main tests passed!")
