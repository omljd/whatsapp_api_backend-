#!/usr/bin/env python3
"""
Create a minimal FastAPI app to test Google Sheets endpoints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from api.google_sheets import router

def create_minimal_app():
    """Create minimal app for testing"""
    
    print("🔧 CREATING MINIMAL TEST APP")
    print("=" * 40)
    
    # Create minimal app
    app = FastAPI(title="Test App")
    
    # Add Google Sheets router
    app.include_router(router, prefix="/api")
    
    # Check routes
    routes = []
    for route in app.routes:
        if hasattr(route, 'routes'):
            for sub_route in route.routes:
                if hasattr(sub_route, 'path'):
                    routes.append(f"{route.path_prefix}{sub_route.path}")
        elif hasattr(route, 'path'):
            routes.append(route.path)
    
    print(f"📊 Total routes: {len(routes)}")
    
    gs_routes = [r for r in routes if 'google-sheets' in r]
    print(f"📊 Google Sheets routes: {len(gs_routes)}")
    
    for route in gs_routes:
        print(f"   📍 {route}")
    
    return app

def test_minimal_app():
    """Test the minimal app"""
    
    print("\n🧪 TESTING MINIMAL APP")
    print("=" * 30)
    
    try:
        app = create_minimal_app()
        
        # Test with uvicorn
        import uvicorn
        
        print("✅ Minimal app created successfully")
        print("💡 Run this command to test:")
        print("   uvicorn minimal_app_test:app --host 0.0.0.0 --port 8001 --reload")
        print("   Then test: http://localhost:8001/api/google-sheets/triggers/history/test")
        
        return app
        
    except Exception as e:
        print(f"❌ Error creating minimal app: {e}")
        return None

if __name__ == "__main__":
    app = test_minimal_app()
    
    if app:
        print("\n🎉 MINIMAL APP READY FOR TESTING")
        print("📝 NEXT STEPS:")
        print("1. Run: uvicorn minimal_app_test:app --host 0.0.0.0 --port 8001 --reload")
        print("2. Test: http://localhost:8001/api/google-sheets/triggers/history/test")
        print("3. If this works, the issue is in main.py startup process")
