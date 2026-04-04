#!/usr/bin/env python3
"""
Test message delivery end-to-end
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the backend path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.unified_service import UnifiedWhatsAppService
from models.device import Device

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_message_delivery():
    """Test message delivery with the working device"""
    
    # Database connection
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/whatsapp_platform')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        logger.info("🚀 STARTING MESSAGE DELIVERY TEST")
        
        # Get the working device (vender login)
        device = db.query(Device).filter(Device.device_name.like("%vender login%")).first()
        if not device:
            logger.error("❌ 'vender login' device not found")
            return False
        
        logger.info(f"✅ Found device: {device.device_name} ({device.device_id})")
        logger.info(f"   Status: {device.session_status}")
        
        # Create unified service
        whatsapp_service = UnifiedWhatsAppService(db)
        
        # Test message with valid phone number format
        test_phone = "+1234567890"  # Use valid format
        test_message = f"Test message from WhatsApp Platform at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        logger.info(f"📤 Sending test message...")
        logger.info(f"   To: {test_phone}")
        logger.info(f"   Message: {test_message}")
        
        # Send message
        response = await whatsapp_service.send_message(
            str(device.device_id), 
            test_phone, 
            test_message
        )
        
        logger.info(f"📥 Response: {response}")
        
        if response.get("success"):
            logger.info("✅ MESSAGE DELIVERY TEST PASSED!")
            logger.info(f"   Message ID: {response.get('message_id')}")
            return True
        else:
            logger.error("❌ MESSAGE DELIVERY TEST FAILED!")
            logger.error(f"   Error: {response.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ EXCEPTION in test: {str(e)}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_message_delivery())
    sys.exit(0 if success else 1)
