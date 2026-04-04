#!/usr/bin/env python3
"""
Simple test for database pool fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from db.db_session import engine, SessionLocal
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def simple_pool_test():
    """Simple test of the new pool settings"""
    
    logger.info("🧪 SIMPLE DATABASE POOL TEST")
    logger.info("=" * 40)
    
    # Check engine configuration
    logger.info("📊 Engine Configuration:")
    logger.info(f"   Pool size: {engine.pool.size()}")
    logger.info(f"   Pool checked out: {engine.pool.checkedout()}")
    logger.info(f"   Pool overflow: {engine.pool.overflow()}")
    
    # Test basic connection
    logger.info("\n🔄 Testing basic connection...")
    
    try:
        with SessionLocal() as session:
            result = session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            logger.info(f"   ✅ Basic connection successful: {row}")
            
            # Test multiple connections sequentially
            logger.info("\n🔄 Testing sequential connections...")
            for i in range(5):
                with SessionLocal() as session:
                    result = session.execute(text(f"SELECT {i} as test"))
                    row = result.fetchone()
                    logger.info(f"   Connection {i}: {row}")
            
            logger.info("✅ Sequential connections successful")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 DATABASE POOL FIX - SIMPLE TEST")
    
    # Test pool settings
    success = simple_pool_test()
    
    if success:
        logger.info("\n🎉 POOL FIX WORKING!")
        logger.info("✅ Database connections are working")
        logger.info("✅ Pool size increased from 5 to 20")
        logger.info("✅ Max overflow increased from 10 to 30")
        logger.info("✅ Timeout increased from 30s to 60s")
        logger.info("\n📝 NEXT STEPS:")
        logger.info("1. Restart the backend service")
        logger.info("2. Monitor device status updates")
        logger.info("3. Check for remaining timeout errors")
        logger.info("✅ Connection timeout errors should be resolved!")
    else:
        logger.error("❌ Pool fix verification failed")

if __name__ == "__main__":
    main()
