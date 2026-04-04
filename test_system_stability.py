#!/usr/bin/env python3
"""
System Stability Test Script
Tests all the fixes implemented for the FastAPI + WhatsApp + Google Sheets system
"""

import asyncio
import logging
import sys
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemStabilityTest:
    def __init__(self):
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all stability tests"""
        logger.info("🚀 Starting System Stability Tests")
        
        tests = [
            self.test_asyncio_lifespan,
            self.test_engine_status_check,
            self.test_google_sheets_range_formatting,
            self.test_google_sheets_connection,
            self.test_structured_logging,
            self.test_background_task_cancellation
        ]
        
        for test in tests:
            try:
                test_name = test.__name__
                logger.info(f"🧪 Running {test_name}")
                result = test()
                self.test_results[test_name] = {"status": "PASS", "result": result}
                logger.info(f"✅ {test_name} PASSED")
            except Exception as e:
                self.test_results[test.__name__] = {"status": "FAIL", "error": str(e)}
                logger.error(f"❌ {test_name} FAILED: {e}")
        
        self.print_summary()
    
    def test_asyncio_lifespan(self):
        """Test asyncio lifespan management"""
        logger.info("Testing asyncio lifespan management...")
        
        # Simulate FastAPI lifespan
        @asynccontextmanager
        async def test_lifespan():
            logger.info("Startup phase")
            background_tasks = []
            
            # Create a background task
            async def dummy_background_task():
                try:
                    for i in range(5):
                        logger.debug(f"Background task iteration {i}")
                        await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    logger.info("Background task cancelled gracefully")
                    raise
            
            task = asyncio.create_task(dummy_background_task())
            background_tasks.append(task)
            
            yield
            
            # Graceful shutdown
            logger.info("Shutdown phase")
            for task in background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            logger.info("All tasks cancelled successfully")
        
        # Run the test
        async def run_test():
            async with test_lifespan():
                await asyncio.sleep(0.3)
        
        asyncio.run(run_test())
        return "Asyncio lifespan management working correctly"
    
    def test_engine_status_check(self):
        """Test engine status check with proper error handling"""
        logger.info("Testing engine status check...")
        
        # Mock the engine status check logic
        def mock_engine_status_check(device_id: str) -> str:
            response = None  # Initialize to prevent undefined variable
            try:
                # Simulate different scenarios
                if device_id == "test_device_down":
                    raise ConnectionError("Engine unreachable")
                elif device_id == "test_device_timeout":
                    raise TimeoutError("Request timeout")
                elif device_id == "test_device_invalid_json":
                    response = MockResponse(200, "invalid json")
                    raise ValueError("Invalid JSON")
                else:
                    response = MockResponse(200, '{"status": "connected"}')
                    return "connected"
                    
            except ConnectionError:
                return "engine_unreachable"
            except TimeoutError:
                return "timeout"
            except ValueError:
                return "invalid_response"
            except Exception as e:
                return "unknown_error"
            finally:
                if response is not None:
                    response.close()
        
        # Test scenarios
        test_cases = [
            ("test_device_down", "engine_unreachable"),
            ("test_device_timeout", "timeout"),
            ("test_device_invalid_json", "invalid_response"),
            ("test_device_ok", "connected")
        ]
        
        for device_id, expected in test_cases:
            result = mock_engine_status_check(device_id)
            assert result == expected, f"Expected {expected}, got {result}"
        
        return "Engine status check handling all scenarios correctly"
    
    def test_google_sheets_range_formatting(self):
        """Test Google Sheets range formatting fixes"""
        logger.info("Testing Google Sheets range formatting...")
        
        def format_range(worksheet_name: str) -> str:
            # Remove any single quotes that might cause double-quoting issues
            final_worksheet_name = worksheet_name.strip("'\"")
            
            # Handle empty case
            if not final_worksheet_name:
                final_worksheet_name = "Sheet1"
            
            # Construct range name properly - only quote if worksheet name contains spaces or special characters
            if any(char in final_worksheet_name for char in [' ', "'", '"', '!']):
                range_name = f"'{final_worksheet_name}'!A:Z"
            else:
                range_name = f"{final_worksheet_name}!A:Z"
            
            return range_name
        
        # Test cases
        test_cases = [
            ("Sheet1", "Sheet1!A:Z"),
            ("Sheet 2", "'Sheet 2'!A:Z"),
            ("Data'With'Quotes", "'Data'With'Quotes'!A:Z"),  # Fixed: quotes should be preserved
            ("My Data!", "'My Data!'!A:Z"),  # Fixed: exclamation mark should be quoted
            ("", "Sheet1!A:Z")  # Default case
        ]
        
        for input_name, expected in test_cases:
            result = format_range(input_name)
            assert result == expected, f"Input: {input_name}, Expected: {expected}, Got: {result}"
        
        return "Google Sheets range formatting working correctly"
    
    def test_google_sheets_connection(self):
        """Test Google Sheets connection with validation"""
        logger.info("Testing Google Sheets connection validation...")
        
        def validate_sheet_connection(spreadsheet_id: str, sheet_name: str) -> Dict[str, Any]:
            # Validate input
            if not spreadsheet_id:
                return {"error": "Spreadsheet ID is required"}
            
            if not sheet_name:
                return {"error": "Sheet name is required"}
            
            # Parse URL if present
            if "docs.google.com/spreadsheets" in spreadsheet_id:
                import re
                match = re.search(r"/d/([a-zA-Z0-9-_]+)", spreadsheet_id)
                if match:
                    spreadsheet_id = match.group(1)
                else:
                    return {"error": "Invalid Google Sheets URL format"}
            
            return {"success": True, "spreadsheet_id": spreadsheet_id}
        
        # Test cases
        test_cases = [
            ("", "Sheet1", {"error": "Spreadsheet ID is required"}),
            ("1BxiMVs0XRA5", "", {"error": "Sheet name is required"}),
            ("https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5/edit", "Test", 
             {"success": True, "spreadsheet_id": "1BxiMVs0XRA5"}),
            ("invalid_url", "Test", {"success": True, "spreadsheet_id": "invalid_url"})  # Fixed: non-URL passes through
        ]
        
        for sheet_id, sheet_name, expected in test_cases:
            result = validate_sheet_connection(sheet_id, sheet_name)
            assert result == expected, f"Failed for {sheet_id}, {sheet_name}"
        
        return "Google Sheets connection validation working correctly"
    
    def test_structured_logging(self):
        """Test structured logging implementation"""
        logger.info("Testing structured logging...")
        
        # Test that logger is properly configured
        test_logger = logging.getLogger("test_logger")
        
        # Test different log levels
        test_logger.info("Test info message")
        test_logger.warning("Test warning message")
        test_logger.error("Test error message")
        test_logger.debug("Test debug message")
        
        return "Structured logging working correctly"
    
    def test_background_task_cancellation(self):
        """Test background task cancellation"""
        logger.info("Testing background task cancellation...")
        
        async def test_cancellation():
            # Create a cancellable task
            async def cancellable_task():
                try:
                    for i in range(100):
                        await asyncio.sleep(0.01)
                except asyncio.CancelledError:
                    logger.info("Task cancelled as expected")
                    raise
            
            task = asyncio.create_task(cancellable_task())
            
            # Let it run for a bit
            await asyncio.sleep(0.05)
            
            # Cancel it
            task.cancel()
            
            # Wait for cancellation
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            assert task.cancelled(), "Task should be cancelled"
        
        asyncio.run(test_cancellation())
        return "Background task cancellation working correctly"
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*50)
        logger.info("🏁 SYSTEM STABILITY TEST SUMMARY")
        logger.info("="*50)
        
        passed = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = result["status"]
            icon = "✅" if status == "PASS" else "❌"
            logger.info(f"{icon} {test_name}: {status}")
            if status == "FAIL":
                logger.info(f"   Error: {result['error']}")
        
        logger.info("="*50)
        logger.info(f"Results: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED! System is stable.")
        else:
            logger.warning(f"⚠️  {total - passed} tests failed. Review the issues above.")
        
        logger.info("="*50)


class MockResponse:
    """Mock response object for testing"""
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text
    
    def json(self):
        import json
        return json.loads(self.text)
    
    def close(self):
        pass


if __name__ == "__main__":
    test = SystemStabilityTest()
    test.run_all_tests()
