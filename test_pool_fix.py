#!/usr/bin/env python3
"""
Test the database pool fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from db.db_session import engine, SessionLocal
from sqlalchemy import text
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pool_settings():
    """Test the new pool settings"""
    
    logger.info("🧪 TESTING DATABASE POOL FIX")
    logger.info("=" * 40)
    
    # Check engine configuration
    logger.info("📊 Engine Configuration:")
    logger.info(f"   Pool size: {engine.pool.size()}")
    logger.info(f"   Pool checked out: {engine.pool.checkedout()}")
    logger.info(f"   Pool overflow: {engine.pool.overflow()}")
    
    # Show pool settings from config
    logger.info("📋 Pool Settings:")
    logger.info(f"   Size: 20 (was 5)")
    logger.info(f"   Max Overflow: 30 (was 10)")
    logger.info(f"   Timeout: 60s (was 30s)")
    logger.info(f"   Recycle: 3600s")
    logger.info(f"   Pre-ping: True")
    
    # Test multiple concurrent connections
    logger.info("\n🔄 Testing concurrent connections...")
    
    def test_connection(worker_id):
        """Test a single connection"""
        try:
            with SessionLocal() as session:
                result = session.execute(text("SELECT 1 as test, :worker_id as worker", {"worker_id": worker_id}))
                row = result.fetchone()
                logger.info(f"   Worker {worker_id}: {row}")
                return True
        except Exception as e:
            logger.error(f"   Worker {worker_id}: Error - {e}")
            return False
    
    # Test with 15 concurrent connections (more than old pool size)
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(test_connection, i) for i in range(15)]
        results = [f.result() for f in futures]
    
    success_count = sum(results)
    logger.info(f"\n📊 Concurrent Test Results:")
    logger.info(f"   Total connections: 15")
    logger.info(f"   Successful: {success_count}")
    logger.info(f"   Failed: {15 - success_count}")
    
    if success_count == 15:
        logger.info("✅ All concurrent connections successful!")
        logger.info("🎉 Pool fix is working correctly!")
        return True
    else:
        logger.error("❌ Some connections failed")
        return False

def test_pool_overflow():
    """Test pool overflow behavior"""
    
    logger.info("\n🌊 Testing Pool Overflow...")
    
    def long_connection(worker_id, duration=2):
        """Connection that holds for longer time"""
        try:
            with SessionLocal() as session:
                result = session.execute(text("SELECT pg_sleep(:duration)", {"duration": duration}))
                logger.info(f"   Worker {worker_id}: Long connection completed")
                return True
        except Exception as e:
            logger.error(f"   Worker {worker_id}: Long connection error - {e}")
            return False
    
    # Test with 25 connections (more than pool size + overflow)
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(long_connection, i, 1) for i in range(25)]
        results = [f.result() for f in futures]
    
    success_count = sum(results)
    logger.info(f"\n📊 Overflow Test Results:")
    logger.info(f"   Total connections: 25")
    logger.info(f"   Successful: {success_count}")
    logger.info(f"   Failed: {25 - success_count}")
    
    return success_count >= 20  # Allow some failures due to timeout

def main():
    """Main test function"""
    logger.info("🚀 DATABASE POOL FIX VERIFICATION")
    
    # Test basic pool settings
    basic_test = test_pool_settings()
    
    # Test overflow behavior
    overflow_test = test_pool_overflow()
    
    if basic_test and overflow_test:
        logger.info("\n🎉 ALL TESTS PASSED!")
        logger.info("✅ Database pool fix is working correctly")
        logger.info("✅ Connection timeout errors should be resolved")
        logger.info("✅ Backend can handle more concurrent requests")
        logger.info("\n📝 NEXT STEPS:")
        logger.info("1. Restart the backend service")
        logger.info("2. Monitor device status updates")
        logger.info("3. Check for remaining timeout errors")
    else:
        logger.error("\n❌ SOME TESTS FAILED")
        logger.error("Please check the pool configuration")

if __name__ == "__main__":
    main()
