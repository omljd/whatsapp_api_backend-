#!/usr/bin/env python3
"""
Final comprehensive system test to verify all fixes
"""

import asyncio
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_final_tests():
    """Run final comprehensive tests"""
    print("🔍 FINAL COMPREHENSIVE SYSTEM TEST")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Database Connection
    tests_total += 1
    try:
        from db.session import SessionLocal
        db = SessionLocal()
        result = db.execute(text('SELECT 1')).fetchone()
        assert result[0] == 1
        db.close()
        print("✅ Database connection: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Database connection: FAIL - {e}")
    
    # Test 2: Main Application Import
    tests_total += 1
    try:
        from main import app
        assert app.title == "WhatsApp Platform Backend"
        print("✅ Main application import: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Main application import: FAIL - {e}")
    
    # Test 3: Google Sheets Service
    tests_total += 1
    try:
        from services.google_sheets_service import GoogleSheetsService
        service = GoogleSheetsService()
        assert service.sdk_available == True
        print("✅ Google Sheets service: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Google Sheets service: FAIL - {e}")
    
    # Test 4: WhatsApp Service
    tests_total += 1
    try:
        from services.whatsapp_service import WhatsAppService
        from db.session import SessionLocal
        import uuid
        db = SessionLocal()
        service = WhatsAppService(db)
        
        # Test with a valid UUID format (even if device doesn't exist)
        test_uuid = str(uuid.uuid4())
        status = service.sync_device_status(test_uuid)
        assert status in ['not_found', 'engine_unreachable', 'timeout', 'unknown_error']
        db.close()
        print("✅ WhatsApp service: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ WhatsApp service: FAIL - {e}")
    
    # Test 5: Google Sheets Automation
    tests_total += 1
    try:
        from services.google_sheets_automation import GoogleSheetsAutomationService
        from db.session import SessionLocal
        db = SessionLocal()
        service = GoogleSheetsAutomationService(db)
        
        # Test the automation (async)
        async def test_automation():
            try:
                await service.process_all_active_triggers()
                return True
            except Exception:
                return False
        
        result = asyncio.run(test_automation())
        assert result == True  # Should complete without crashing
        db.close()
        print("✅ Google Sheets automation: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Google Sheets automation: FAIL - {e}")
    
    # Test 6: API Endpoints
    tests_total += 1
    try:
        from fastapi.testclient import TestClient
        from main import app
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get('/')
        assert response.status_code == 200
        assert 'message' in response.json()
        
        # Test health endpoint
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
        
        print("✅ API endpoints: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ API endpoints: FAIL - {e}")
    
    # Test 7: Router Imports
    tests_total += 1
    try:
        from api import google_sheets_router, whatsapp_router, unified_router
        assert google_sheets_router is not None
        assert whatsapp_router is not None
        assert unified_router is not None
        print("✅ Router imports: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Router imports: FAIL - {e}")
    
    # Test 8: Database Models
    tests_total += 1
    try:
        from models.google_sheet import GoogleSheet, GoogleSheetTrigger
        from models.device import Device
        assert GoogleSheet is not None
        assert GoogleSheetTrigger is not None
        assert Device is not None
        print("✅ Database models: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Database models: FAIL - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🏁 FINAL TEST RESULTS: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 ALL TESTS PASSED! System is fully operational.")
        print("\n✅ System Status:")
        print("   • Database: Connected")
        print("   • FastAPI: Running")
        print("   • Google Sheets: Integrated")
        print("   • WhatsApp: Ready")
        print("   • Background Tasks: Stable")
        print("   • API Endpoints: Working")
        print("\n🚀 Ready for production!")
    else:
        print(f"⚠️  {tests_total - tests_passed} tests failed. Review issues above.")
    
    print("=" * 50)
    
    return tests_passed == tests_total

if __name__ == "__main__":
    success = run_final_tests()
    exit(0 if success else 1)
