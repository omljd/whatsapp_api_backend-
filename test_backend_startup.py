#!/usr/bin/env python3
"""
Test backend startup and endpoint availability
"""

import requests
import time
import subprocess
import sys
import os

def test_backend_health():
    """Test if backend is healthy"""
    
    print("🔍 TESTING BACKEND HEALTH")
    print("=" * 40)
    
    # Test basic health endpoints
    endpoints = [
        ("http://localhost:8000/docs", "API Documentation"),
        ("http://localhost:8000/openapi.json", "OpenAPI Schema"),
        ("http://localhost:8000/api/google-sheets/triggers/history/test", "Test Trigger History"),
        ("http://localhost:8000/api/google-sheets/", "List Sheets"),
    ]
    
    results = {}
    
    for url, description in endpoints:
        print(f"\n📡 Testing: {url}")
        print(f"📝 {description}")
        
        try:
            response = requests.get(url, timeout=10)
            status = response.status_code
            results[url] = status
            
            if status == 200:
                print(f"✅ SUCCESS: {status}")
                if 'json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        if 'data' in data:
                            print(f"📊 Records: {len(data['data'])}")
                        else:
                            print(f"📊 Response size: {len(str(data))} chars")
                    except:
                        pass
            elif status == 404:
                print(f"❌ NOT FOUND: {status}")
                print(f"📄 Response: {response.text}")
            elif status == 400:
                print(f"❌ BAD REQUEST: {status}")
                print(f"📄 Response: {response.text}")
            elif status == 401:
                print(f"🔒 UNAUTHORIZED: {status}")
            else:
                print(f"❌ ERROR: {status}")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: Backend not responding")
            results[url] = "TIMEOUT"
        except requests.exceptions.ConnectionError:
            print(f"🔌 CONNECTION ERROR: Backend not running")
            results[url] = "CONNECTION_ERROR"
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results[url] = "ERROR"
    
    return results

def test_database_connection():
    """Test database connection directly"""
    
    print("\n🔍 TESTING DATABASE CONNECTION")
    print("=" * 40)
    
    try:
        sys.path.append(os.path.dirname(__file__))
        from db.base import engine
        from sqlalchemy import text
        
        print("🔌 Testing database engine...")
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            print(f"✅ Database connection successful: {test_value}")
            
            # Test pool settings
            print(f"📊 Pool size: {engine.pool.size()}")
            print(f"📊 Pool overflow: {engine.pool.overflow()}")
            print(f"📊 Pool checked out: {engine.pool.checkedout()}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_app_import():
    """Test if the app can be imported"""
    
    print("\n🔍 TESTING APP IMPORT")
    print("=" * 30)
    
    try:
        sys.path.append(os.path.dirname(__file__))
        from main import app
        
        print("✅ App imported successfully")
        
        # Check routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'routes'):
                for sub_route in route.routes:
                    if hasattr(sub_route, 'path'):
                        routes.append(f"{route.path_prefix}{sub_route.path}")
            elif hasattr(route, 'path'):
                routes.append(route.path)
        
        gs_routes = [r for r in routes if 'google-sheets' in r]
        print(f"📊 Total routes: {len(routes)}")
        print(f"📊 Google Sheets routes: {len(gs_routes)}")
        
        for route in gs_routes[:5]:  # Show first 5
            print(f"   📍 {route}")
        
        return len(gs_routes) > 0
        
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def diagnose_startup_issues():
    """Diagnose startup issues"""
    
    print("\n🔧 DIAGNOSING STARTUP ISSUES")
    print("=" * 40)
    
    issues = []
    
    # Test database connection
    if not test_database_connection():
        issues.append("Database connection failed")
    
    # Test app import
    if not test_app_import():
        issues.append("App import failed")
    
    # Test backend health
    results = test_backend_health()
    
    # Check for specific issues
    if "http://localhost:8000/docs" in results and results["http://localhost:8000/docs"] == 200:
        print("✅ Basic FastAPI is working")
        
        if "http://localhost:8000/api/google-sheets/triggers/history/test" in results:
            gs_status = results["http://localhost:8000/api/google-sheets/triggers/history/test"]
            if gs_status == 404:
                issues.append("Google Sheets router not registered")
            elif gs_status == "TIMEOUT":
                issues.append("Backend hanging on Google Sheets endpoints")
    else:
        issues.append("FastAPI not responding")
    
    return issues

def main():
    """Main diagnostic function"""
    print("🚀 BACKEND STARTUP DIAGNOSTIC")
    print("=" * 50)
    
    issues = diagnose_startup_issues()
    
    print("\n" + "=" * 50)
    print("📋 DIAGNOSIS RESULTS:")
    
    if not issues:
        print("✅ No issues found - backend should be working")
        print("\n💡 If frontend still gets 400 errors:")
        print("   1. Check authentication token")
        print("   2. Check frontend API calls")
        print("   3. Check CORS configuration")
    else:
        print("❌ Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 RECOMMENDED FIXES:")
        if "Database connection failed" in issues:
            print("   1. Check database URL in core/config.py")
            print("   2. Verify database is accessible")
            print("   3. Check pool settings")
        
        if "App import failed" in issues:
            print("   1. Check for import errors in main.py")
            print("   2. Verify all dependencies are installed")
            print("   3. Check for circular imports")
        
        if "Google Sheets router not registered" in issues:
            print("   1. Check google_sheets_router import in main.py")
            print("   2. Verify app.include_router call")
            print("   3. Check for router import errors")
        
        if "Backend hanging on Google Sheets endpoints" in issues:
            print("   1. Check database connection in Google Sheets endpoints")
            print("   2. Look for infinite loops or blocking operations")
            print("   3. Check for dependency injection issues")

if __name__ == "__main__":
    main()
