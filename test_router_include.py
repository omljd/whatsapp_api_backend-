#!/usr/bin/env python3
"""
Test router inclusion directly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_router_include():
    """Test router inclusion directly"""
    
    print("🧪 TESTING ROUTER INCLUSION")
    print("=" * 40)
    
    try:
        from fastapi import FastAPI
        from api import google_sheets_router
        
        # Create test app
        app = FastAPI()
        
        print(f"📊 Initial app routes: {len(app.routes)}")
        
        # Include router
        app.include_router(google_sheets_router, prefix="/api")
        
        print(f"📊 Routes after include: {len(app.routes)}")
        
        # Check for Google Sheets routes
        gs_routes = []
        for route in app.routes:
            if hasattr(route, 'path_prefix') and hasattr(route, 'routes'):
                # This is an included router
                for sub_route in route.routes:
                    if hasattr(sub_route, 'path'):
                        full_path = f"{route.path_prefix}{sub_route.path}"
                        if 'google-sheets' in full_path:
                            gs_routes.append(full_path)
            elif hasattr(route, 'path'):
                if 'google-sheets' in route.path:
                    gs_routes.append(route.path)
        
        print(f"📊 Google Sheets routes found: {len(gs_routes)}")
        
        for route in gs_routes[:5]:
            print(f"   📍 {route}")
        
        return len(gs_routes) > 0
        
    except Exception as e:
        print(f"❌ Error testing router inclusion: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_app_routes():
    """Test the main app routes"""
    
    print("\n🔍 TESTING MAIN APP ROUTES")
    print("=" * 35)
    
    try:
        from main import app
        
        print(f"📊 Main app routes: {len(app.routes)}")
        
        # Find Google Sheets router
        gs_router_found = False
        for route in app.routes:
            if hasattr(route, 'path_prefix'):
                print(f"   📍 Router prefix: {route.path_prefix}")
                if 'google-sheets' in str(route):
                    gs_router_found = True
                    print(f"   ✅ Google Sheets router found!")
                    if hasattr(route, 'routes'):
                        print(f"   📊 Sub-routes: {len(route.routes)}")
        
        if not gs_router_found:
            print("   ❌ Google Sheets router not found in app")
        
        return gs_router_found
        
    except Exception as e:
        print(f"❌ Error testing main app: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_include_process():
    """Debug the include process step by step"""
    
    print("\n🔧 DEBUGGING INCLUDE PROCESS")
    print("=" * 40)
    
    try:
        # Step 1: Import router
        print("📦 Step 1: Importing router...")
        from api import google_sheets_router
        print(f"   ✅ Router imported: {type(google_sheets_router)}")
        print(f"   📊 Routes: {len(google_sheets_router.routes)}")
        
        # Step 2: Create app
        print("\n🏗️  Step 2: Creating app...")
        from fastapi import FastAPI
        app = FastAPI()
        print(f"   ✅ App created: {type(app)}")
        print(f"   📊 Initial routes: {len(app.routes)}")
        
        # Step 3: Include router
        print("\n🔗 Step 3: Including router...")
        app.include_router(google_sheets_router, prefix="/api")
        print(f"   ✅ Router included")
        print(f"   📊 Routes after include: {len(app.routes)}")
        
        # Step 4: Check routes
        print("\n🔍 Step 4: Checking routes...")
        gs_count = 0
        for route in app.routes:
            if hasattr(route, 'path_prefix'):
                print(f"   📍 Router: {route.path_prefix}")
                if hasattr(route, 'routes'):
                    for sub_route in route.routes:
                        if hasattr(sub_route, 'path'):
                            full_path = f"{route.path_prefix}{sub_route.path}"
                            if 'google-sheets' in full_path:
                                gs_count += 1
                                print(f"      ✅ {full_path}")
        
        print(f"\n📊 Google Sheets routes found: {gs_count}")
        
        return gs_count > 0
        
    except Exception as e:
        print(f"❌ Error in debug process: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 ROUTER INCLUSION DEBUG")
    print("=" * 50)
    
    # Test router inclusion
    include_ok = test_router_include()
    
    # Test main app
    main_ok = test_main_app_routes()
    
    # Debug process
    debug_ok = debug_include_process()
    
    print("\n" + "=" * 50)
    print("📋 RESULTS:")
    print(f"✅ Router inclusion test: {include_ok}")
    print(f"✅ Main app test: {main_ok}")
    print(f"✅ Debug process: {debug_ok}")
    
    if include_ok and not main_ok:
        print("\n💡 ISSUE: Router inclusion works but main app doesn't have routes")
        print("   This suggests an error during main app startup")
        print("   Check main.py for errors during app.include_router()")
    
    elif not include_ok:
        print("\n💡 ISSUE: Router inclusion itself is failing")
        print("   Check for router definition issues")
    
    else:
        print("\n✅ Everything looks good - router should be working")

if __name__ == "__main__":
    main()
