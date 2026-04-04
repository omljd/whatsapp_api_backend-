#!/usr/bin/env python3
"""
Test database connection with the provided credentials
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
import logging

# Database connection details from user
DATABASE_URL = "postgresql://whatsapp_platform_fn0k_user:AbHezwfAs553dVCy33wfHzsGMVJbf8M0@dpg-d6oh8tfafjfc7386oii0-a.oregon-postgres.render.com/whatsapp_platform_fn0k"

# Create engine
engine = create_engine(DATABASE_URL)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test database connection and show basic info"""
    try:
        logger.info("🔗 Testing database connection...")
        logger.info(f"📍 Host: dpg-d6oh8tfafjfc7386oii0-a.oregon-postgres.render.com")
        logger.info(f"🗄️  Database: whatsapp_platform_fn0k")
        logger.info(f"👤 User: whatsapp_platform_fn0k_user")
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"✅ Connection successful!")
            logger.info(f"📊 PostgreSQL Version: {version}")
            
            # Check current database
            result = conn.execute(text("SELECT current_database()"))
            current_db = result.scalar()
            logger.info(f"🗄️  Current Database: {current_db}")
            
            # Check current user
            result = conn.execute(text("SELECT current_user"))
            current_user = result.scalar()
            logger.info(f"👤 Current User: {current_user}")
            
            # Count tables
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            logger.info(f"📋 Total Tables: {table_count}")
            
            # Show table names
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            logger.info("📋 Tables in database:")
            for table in tables:
                logger.info(f"  ✅ {table}")
                
            logger.info("")
            logger.info("🎉 Database connection test completed successfully!")
            logger.info("✅ All credentials are working correctly")
            logger.info("✅ Database is ready for use")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_psql_command():
    """Show the PSQL command for manual connection"""
    logger.info("")
    logger.info("🔧 PSQL Command for manual connection:")
    logger.info("PGPASSWORD=AbHezwfAs553dVCy33wfHzsGMVJbf8M0 psql -h dpg-d6oh8tfafjfc7386oii0-a.oregon-postgres.render.com -U whatsapp_platform_fn0k_user whatsapp_platform_fn0k")

def main():
    """Main function"""
    logger.info("🎯 DATABASE CONNECTION TEST")
    logger.info("=" * 50)
    
    if test_connection():
        test_psql_command()
    else:
        logger.error("❌ Connection test failed - please check credentials")

if __name__ == "__main__":
    main()
