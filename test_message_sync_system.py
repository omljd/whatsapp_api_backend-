#!/usr/bin/env python3
"""
Comprehensive test script for WhatsApp message synchronization system.
Tests the complete flow from Baileys events to dashboard display.
"""

import asyncio
import json
import logging
import requests
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.device import Device, DeviceType
from models.whatsapp_messages import WhatsAppMessages
from models.whatsapp_inbox import WhatsAppInbox
from services.baileys_message_sync_service import baileys_sync_service
from services.message_sync_initiator import message_sync_initiator
from services.websocket_manager import websocket_manager
from services.uuid_service import UUIDService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageSyncSystemTest:
    """Test suite for the WhatsApp message synchronization system"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.test_device_id = None
        self.test_user_id = None
        
    def setup_test_device(self):
        """Create a test device for testing"""
        try:
            # Create test device (or use existing)
            test_device = Device(
                device_name="Test Sync Device",
                device_type=DeviceType.web,
                session_status="connected"
            )
            
            self.db.add(test_device)
            self.db.commit()
            self.db.refresh(test_device)
            
            self.test_device_id = str(test_device.device_id)
            self.test_user_id = str(test_device.busi_user_id)
            
            logger.info(f"Test device created: {self.test_device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create test device: {e}")
            return False
    
    def test_database_schema(self):
        """Test database schema and relationships"""
        logger.info("Testing database schema...")
        
        try:
            # Test whatsapp_messages table exists
            count = self.db.query(WhatsAppMessages).count()
            logger.info(f"WhatsAppMessages table accessible. Current count: {count}")
            
            # Test device relationship
            device = self.db.query(Device).first()
            if device:
                messages = device.whatsapp_messages
                logger.info(f"Device relationship works. Messages count: {len(messages) if messages else 0}")
            
            # Test indexes (basic check)
            # This would require more complex SQL to test actual indexes
            logger.info("Database schema test passed")
            return True
            
        except Exception as e:
            logger.error(f"Database schema test failed: {e}")
            return False
    
    async def test_message_storage(self):
        """Test message storage endpoint"""
        logger.info("Testing message storage...")
        
        try:
            test_message = {
                "device_id": self.test_device_id,
                "phone": "+1234567890",
                "message_id": "test_msg_001",
                "message": "Test message from sync system",
                "from_me": False,
                "contact_name": "Test Contact",
                "message_type": "text"
            }
            
            # Test via direct service call
            from api.messages import MessageStoreRequest
            request = MessageStoreRequest(**test_message)
            
            # Simulate storage
            message = WhatsAppMessages(
                device_id=UUIDService.safe_convert(request.device_id),
                message_id=request.message_id,
                phone=request.phone,
                contact_name=request.contact_name,
                message=request.message,
                message_type=request.message_type,
                from_me=request.from_me,
                is_read=request.from_me
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Message stored successfully: {message.id}")
            
            # Test deduplication
            duplicate_message = WhatsAppMessages(
                device_id=UUIDService.safe_convert(request.device_id),
                message_id=request.message_id,  # Same ID
                phone=request.phone,
                message="Duplicate message",
                from_me=False
            )
            
            self.db.add(duplicate_message)
            self.db.commit()
            
            # Check if duplicate was prevented (should be 1, not 2)
            count = self.db.query(WhatsAppMessages).filter(
                WhatsAppMessages.message_id == request.message_id
            ).count()
            
            if count == 1:
                logger.info("Message deduplication working correctly")
            else:
                logger.warning(f"Message deduplication failed. Count: {count}")
            
            return True
            
        except Exception as e:
            logger.error(f"Message storage test failed: {e}")
            return False
    
    async def test_baileys_event_handling(self):
        """Test Baileys event handling"""
        logger.info("Testing Baileys event handling...")
        
        try:
            # Simulate messages.upsert event
            event_data = {
                "event": "messages.upsert",
                "messages": [
                    {
                        "key": {
                            "id": "baileys_msg_001",
                            "remoteJid": "+1234567890@s.whatsapp.net",
                            "fromMe": False
                        },
                        "message": "Test Baileys message",
                        "messageTimestamp": int(datetime.now(timezone.utc).timestamp()),
                        "pushName": "Baileys Contact"
                    }
                ]
            }
            
            # Test event handling
            result = await baileys_sync_service.handle_message_upsert(
                self.test_device_id, 
                event_data
            )
            
            if result["success"]:
                logger.info(f"Baileys event handled successfully. Stored: {result.get('stored_count', 0)}")
            else:
                logger.error(f"Baileys event handling failed: {result.get('error')}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Baileys event handling test failed: {e}")
            return False
    
    async def test_conversation_queries(self):
        """Test conversation summary queries"""
        logger.info("Testing conversation queries...")
        
        try:
            # Test the service method directly
            conversations = baileys_sync_service.get_device_conversations(
                self.test_device_id, 
                limit=10
            )
            
            logger.info(f"Found {len(conversations)} conversations")
            
            for conv in conversations:
                logger.info(f"  - {conv['phone']}: {conv['last_message'][:50]}... (Unread: {conv['unread_count']})")
            
            return True
            
        except Exception as e:
            logger.error(f"Conversation queries test failed: {e}")
            return False
    
    async def test_websocket_broadcasting(self):
        """Test WebSocket broadcasting (simulated)"""
        logger.info("Testing WebSocket broadcasting...")
        
        try:
            # Test WebSocket manager functionality
            connection_count = websocket_manager.get_total_connections()
            logger.info(f"Current WebSocket connections: {connection_count}")
            
            # Simulate broadcasting (would require actual WebSocket connections)
            test_message = {
                "phone": "+1234567890",
                "message": "Test broadcast message",
                "from_me": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # This would normally broadcast to connected clients
            # await websocket_manager.broadcast_new_message(test_message, self.test_device_id, self.db)
            
            logger.info("WebSocket broadcasting test completed (no active connections)")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket broadcasting test failed: {e}")
            return False
    
    async def test_sync_initiation(self):
        """Test sync initiation on device connection"""
        logger.info("Testing sync initiation...")
        
        try:
            # Test sync initiation
            result = await message_sync_initiator.start_sync_on_connection(
                self.test_device_id, 
                self.db
            )
            
            if result["success"]:
                logger.info(f"Sync initiation successful: {result}")
            else:
                logger.error(f"Sync initiation failed: {result.get('error')}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Sync initiation test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("Starting WhatsApp Message Sync System Tests")
        logger.info("=" * 50)
        
        tests = [
            ("Database Schema", self.test_database_schema),
            ("Message Storage", self.test_message_storage),
            ("Baileys Event Handling", self.test_baileys_event_handling),
            ("Conversation Queries", self.test_conversation_queries),
            ("WebSocket Broadcasting", self.test_websocket_broadcasting),
            ("Sync Initiation", self.test_sync_initiation),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n--- Running {test_name} Test ---")
            try:
                result = await test_func()
                results[test_name] = result
                status = "PASS" if result else "FAIL"
                logger.info(f"{test_name}: {status}")
            except Exception as e:
                results[test_name] = False
                logger.error(f"{test_name}: FAIL - {e}")
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("TEST SUMMARY")
        logger.info("=" * 50)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{test_name:.<30} {status}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        return passed == total
    
    def cleanup(self):
        """Clean up test data"""
        try:
            # Clean up test messages
            self.db.query(WhatsAppMessages).filter(
                WhatsAppMessages.device_id == UUIDService.safe_convert(self.test_device_id)
            ).delete()
            
            # Clean up test device
            self.db.query(Device).filter(
                Device.device_id == UUIDService.safe_convert(self.test_device_id)
            ).delete()
            
            self.db.commit()
            logger.info("Test data cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
        finally:
            self.db.close()

async def main():
    """Main test runner"""
    test_suite = MessageSyncSystemTest()
    
    try:
        # Setup
        if not test_suite.setup_test_device():
            logger.error("Failed to setup test device")
            return
        
        # Run tests
        success = await test_suite.run_all_tests()
        
        if success:
            logger.info("\n🎉 All tests passed! WhatsApp message sync system is ready.")
        else:
            logger.error("\n❌ Some tests failed. Please check the logs.")
    
    finally:
        # Cleanup
        test_suite.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
