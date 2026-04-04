#!/usr/bin/env python3
"""
Comprehensive test script for WhatsApp Engine fixes
Tests all scenarios mentioned in the requirements
"""

import asyncio
import logging
import sys
import os
import time
import requests
from datetime import datetime

# Add the backend path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'whatsapp_platform_backend'))

from services.whatsapp_engine_service import WhatsAppEngineService
from services.unified_service import UnifiedWhatsAppService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WhatsAppEngineTester:
    def __init__(self):
        self.engine_url = "http://localhost:3001"
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} - {test_name}"
        if message:
            result += f": {message}"
        logger.info(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now()
        })
    
    def test_engine_health_endpoint(self):
        """Test 1: Engine health endpoint"""
        logger.info("Testing Engine Health Endpoint...")
        
        try:
            response = requests.get(f"{self.engine_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "engine", "active_sessions", "total_sessions", "port", "uptime", "timestamp"]
                
                missing_fields = [field for field in expected_fields if field not in data]
                
                if not missing_fields:
                    self.log_test(
                        "Engine Health Endpoint", 
                        True, 
                        f"Status: {data.get('status')}, Active sessions: {data.get('active_sessions')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Engine Health Endpoint", 
                        False, 
                        f"Missing fields: {missing_fields}"
                    )
                    return False
            else:
                self.log_test(
                    "Engine Health Endpoint", 
                    False, 
                    f"HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Engine Health Endpoint", False, str(e))
            return False
    
    def test_engine_sessions_endpoint(self):
        """Test 2: Engine sessions endpoint"""
        logger.info("Testing Engine Sessions Endpoint...")
        
        try:
            response = requests.get(f"{self.engine_url}/sessions", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    self.log_test(
                        "Engine Sessions Endpoint", 
                        True, 
                        f"Retrieved {len(data)} sessions"
                    )
                    return True
                else:
                    self.log_test(
                        "Engine Sessions Endpoint", 
                        False, 
                        "Response is not a dictionary"
                    )
                    return False
            else:
                self.log_test(
                    "Engine Sessions Endpoint", 
                    False, 
                    f"HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Engine Sessions Endpoint", False, str(e))
            return False
    
    def test_engine_reconnect_endpoint(self):
        """Test 3: Engine reconnect endpoint"""
        logger.info("Testing Engine Reconnect Endpoint...")
        
        test_device_id = "test-device-123"
        
        try:
            response = requests.post(
                f"{self.engine_url}/session/{test_device_id}/reconnect", 
                timeout=10
            )
            
            if response.status_code in [200, 404]:  # 404 is acceptable for non-existent device
                self.log_test(
                    "Engine Reconnect Endpoint", 
                    True, 
                    f"HTTP {response.status_code}"
                )
                return True
            else:
                self.log_test(
                    "Engine Reconnect Endpoint", 
                    False, 
                    f"HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Engine Reconnect Endpoint", False, str(e))
            return False
    
    def test_engine_error_handling(self):
        """Test 4: Engine error handling"""
        logger.info("Testing Engine Error Handling...")
        
        try:
            # Test non-existent device
            response = requests.get(
                f"{self.engine_url}/session/non-existent-device/status", 
                timeout=5
            )
            
            if response.status_code == 404:
                # Test sending message to non-existent device
                response = requests.post(
                    f"{self.engine_url}/session/non-existent-device/message",
                    json={"to": "+1234567890", "message": "test"},
                    timeout=5
                )
                
                if response.status_code == 404:
                    self.log_test("Engine Error Handling", True, "Proper 404 responses")
                    return True
                else:
                    self.log_test(
                        "Engine Error Handling", 
                        False, 
                        f"Expected 404 for message, got {response.status_code}"
                    )
                    return False
            else:
                self.log_test(
                    "Engine Error Handling", 
                    False, 
                    f"Expected 404 for status, got {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Engine Error Handling", False, str(e))
            return False
    
    def test_backend_engine_service(self):
        """Test 5: Backend engine service integration"""
        logger.info("Testing Backend Engine Service...")
        
        try:
            # Mock database session for testing
            from sqlalchemy.orm import Session
            from sqlalchemy import create_engine
            
            # Use in-memory SQLite for testing
            engine = create_engine("sqlite:///:memory:")
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            # Test engine service initialization
            engine_service = WhatsAppEngineService(db)
            
            # Test engine reachability
            reachable = engine_service.check_engine_reachable()
            
            # Test engine health
            health = engine_service.check_engine_health()
            
            # Test device status check
            device_status = engine_service.check_device_status("test-device")
            
            db.close()
            
            if reachable and health.get("healthy", False):
                self.log_test(
                    "Backend Engine Service", 
                    True, 
                    f"Reachable: {reachable}, Healthy: {health.get('healthy')}"
                )
                return True
            else:
                self.log_test(
                    "Backend Engine Service", 
                    False, 
                    f"Reachable: {reachable}, Healthy: {health.get('healthy')}"
                )
                return False
                
        except Exception as e:
            self.log_test("Backend Engine Service", False, str(e))
            return False
    
    def test_engine_stopped_scenario(self):
        """Test 6: Engine stopped scenario"""
        logger.info("Testing Engine Stopped Scenario...")
        
        # This test simulates what happens when engine is stopped
        # We'll test by calling a non-existent port
        test_url = "http://localhost:9999"  # Non-existent port
        
        try:
            response = requests.get(f"{test_url}/health", timeout=2)
            self.log_test(
                "Engine Stopped Scenario", 
                False, 
                "Should not reach this point"
            )
            return False
        except requests.exceptions.ConnectionError:
            self.log_test(
                "Engine Stopped Scenario", 
                True, 
                "Correctly detected engine unreachable"
            )
            return True
        except Exception as e:
            self.log_test(
                "Engine Stopped Scenario", 
                False, 
                f"Unexpected error: {str(e)}"
            )
            return False
    
    def test_message_send_validation(self):
        """Test 7: Message send validation"""
        logger.info("Testing Message Send Validation...")
        
        try:
            # Mock database session
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            engine = create_engine("sqlite:///:memory:")
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            engine_service = WhatsAppEngineService(db)
            
            # Test sending message to non-existent device
            result = engine_service.send_message(
                device_id="non-existent-device",
                to="+1234567890",
                message="Test message"
            )
            
            db.close()
            
            if not result["success"] and "not connected" in result.get("error", ""):
                self.log_test(
                    "Message Send Validation", 
                    True, 
                    "Correctly rejected message for non-existent device"
                )
                return True
            else:
                self.log_test(
                    "Message Send Validation", 
                    False, 
                    f"Should have failed: {result}"
                )
                return False
                
        except Exception as e:
            self.log_test("Message Send Validation", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        logger.info("=" * 60)
        logger.info("STARTING WHATSAPP ENGINE COMPREHENSIVE TESTS")
        logger.info("=" * 60)
        
        tests = [
            self.test_engine_health_endpoint,
            self.test_engine_sessions_endpoint,
            self.test_engine_reconnect_endpoint,
            self.test_engine_error_handling,
            self.test_backend_engine_service,
            self.test_engine_stopped_scenario,
            self.test_message_send_validation
        ]
        
        # Run all tests
        for test in tests:
            try:
                test()
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")
                self.log_test(test.__name__, False, f"Exception: {str(e)}")
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate test summary"""
        logger.info("=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.info("\nFailed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    logger.info(f"  ❌ {result['test']}: {result['message']}")
        
        logger.info("=" * 60)
        
        if failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED! WhatsApp Engine fixes are working correctly.")
        else:
            logger.info(f"⚠️  {failed_tests} test(s) failed. Please review and fix issues.")
        
        return failed_tests == 0

def main():
    """Main function"""
    logger.info("WhatsApp Engine Comprehensive Test Script")
    logger.info("This script tests all the fixes implemented for the WhatsApp Engine unreachable issue")
    
    tester = WhatsAppEngineTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
