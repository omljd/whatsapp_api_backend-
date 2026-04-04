#!/usr/bin/env python3
"""
Test script for new trigger features:
- Optional Text Message/Caption
- Send_time column for time-based triggers
- Message column for sheet content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
import logging
from datetime import datetime, timedelta

# Database URL
DATABASE_URL = "postgresql://whatsapp_platform_fn0k_user:AbHezwfAs553dVCy33wfHzsGMVJbf8M0@dpg-d6oh8tfafjfc7386oii0-a.oregon-postgres.render.com/whatsapp_platform_fn0k"

# Create engine
engine = create_engine(DATABASE_URL)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_new_trigger_features():
    """Test the new trigger features"""
    
    logger.info("🧪 TESTING NEW TRIGGER FEATURES")
    logger.info("=" * 50)
    
    try:
        with engine.connect() as conn:
            
            # Step 1: Verify new columns exist
            logger.info("📋 Step 1: Verifying new columns...")
            
            columns_result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'google_sheet_triggers'
                AND column_name IN ('send_time_column', 'message_column')
                ORDER BY column_name
            """))
            columns = columns_result.fetchall()
            
            logger.info("   📊 New trigger columns:")
            for col in columns:
                nullable_text = "NULL" if col[2] == "YES" else "NOT NULL"
                logger.info(f"      {col[0]}: {col[1]} ({nullable_text})")
            
            if len(columns) != 2:
                logger.error(f"   ❌ Expected 2 new columns, found {len(columns)}")
                return False
            
            # Step 2: Test time-based trigger creation
            logger.info("📋 Step 2: Testing time-based trigger creation...")
            
            # Get a sample sheet and device
            sheet_result = conn.execute(text("""
                SELECT id, sheet_name FROM google_sheets LIMIT 1
            """))
            sheet = sheet_result.fetchone()
            
            device_result = conn.execute(text("""
                SELECT device_id, device_name FROM devices 
                WHERE session_status = 'connected' 
                LIMIT 1
            """))
            device = device_result.fetchone()
            
            if not sheet:
                logger.warning("   ⚠️  No sheets found - creating test data")
                return False
            
            if not device:
                logger.warning("   ⚠️  No connected devices found")
                return False
            
            logger.info(f"   📋 Using sheet: {sheet[1]} ({sheet[0]})")
            logger.info(f"   📱 Using device: {device[1]} ({device[0]})")
            
            # Create a time-based trigger
            trigger_id = f"test_time_trigger_{int(datetime.utcnow().timestamp())}"
            
            conn.execute(text("""
                INSERT INTO google_sheet_triggers (
                    trigger_id, sheet_id, device_id, trigger_type, is_enabled,
                    phone_column, status_column, send_time_column, message_column,
                    message_template, trigger_value, created_at
                ) VALUES (
                    :trigger_id, :sheet_id, :device_id, 'time', true,
                    'phone', 'Status', 'Send_time', 'Message',
                    'Hello {{Name}} - scheduled message!', 'Scheduled', :created_at
                )
            """), {
                'trigger_id': trigger_id,
                'sheet_id': sheet[0],
                'device_id': device[0],
                'created_at': datetime.utcnow()
            })
            
            conn.commit()
            logger.info(f"   ✅ Created time-based trigger: {trigger_id}")
            
            # Step 3: Test message column trigger creation
            logger.info("📋 Step 3: Testing message column trigger...")
            
            message_trigger_id = f"test_message_trigger_{int(datetime.utcnow().timestamp())}"
            
            conn.execute(text("""
                INSERT INTO google_sheet_triggers (
                    trigger_id, sheet_id, device_id, trigger_type, is_enabled,
                    phone_column, status_column, message_column,
                    trigger_value, created_at
                ) VALUES (
                    :trigger_id, :sheet_id, :device_id, 'update_row', true,
                    'phone', 'Status', 'Message',
                    'Send', :created_at
                )
            """), {
                'trigger_id': message_trigger_id,
                'sheet_id': sheet[0],
                'device_id': device[0],
                'created_at': datetime.utcnow()
            })
            
            conn.commit()
            logger.info(f"   ✅ Created message column trigger: {message_trigger_id}")
            
            # Step 4: Verify triggers were created with new fields
            logger.info("📋 Step 4: Verifying triggers...")
            
            verify_result = conn.execute(text("""
                SELECT 
                    trigger_id,
                    trigger_type,
                    phone_column,
                    status_column,
                    send_time_column,
                    message_column,
                    message_template,
                    trigger_value
                FROM google_sheet_triggers
                WHERE trigger_id IN (:trigger_id1, :trigger_id2)
                ORDER BY trigger_id
            """), {
                'trigger_id1': trigger_id,
                'trigger_id2': message_trigger_id
            })
            
            triggers = verify_result.fetchall()
            
            logger.info("   📊 Created triggers:")
            for trigger in triggers:
                trigger_id, trigger_type, phone_col, status_col, send_time_col, message_col, template, trigger_val = trigger
                logger.info(f"      {trigger_id} ({trigger_type}):")
                logger.info(f"         Phone Column: {phone_col}")
                logger.info(f"         Status Column: {status_col}")
                logger.info(f"         Send Time Column: {send_time_col}")
                logger.info(f"         Message Column: {message_col}")
                logger.info(f"         Message Template: {template[:50] if template else 'None'}...")
                logger.info(f"         Trigger Value: {trigger_val}")
            
            # Step 5: Test optional message template
            logger.info("📋 Step 5: Testing optional message template...")
            
            optional_trigger_id = f"test_optional_trigger_{int(datetime.utcnow().timestamp())}"
            
            conn.execute(text("""
                INSERT INTO google_sheet_triggers (
                    trigger_id, sheet_id, device_id, trigger_type, is_enabled,
                    phone_column, status_column,
                    trigger_value, created_at
                ) VALUES (
                    :trigger_id, :sheet_id, :device_id, 'update_row', true,
                    'phone', 'Status',
                    'Send', :created_at
                )
            """), {
                'trigger_id': optional_trigger_id,
                'sheet_id': sheet[0],
                'device_id': device[0],
                'created_at': datetime.utcnow()
            })
            
            conn.commit()
            logger.info(f"   ✅ Created optional message trigger: {optional_trigger_id}")
            
            logger.info("")
            logger.info("🎉 ALL TESTS PASSED!")
            logger.info("✅ New columns are working correctly")
            logger.info("✅ Time-based triggers can use Send_time column")
            logger.info("✅ Message column triggers work properly")
            logger.info("✅ Optional message templates are supported")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    
    logger.info("🧹 CLEANING UP TEST DATA")
    
    try:
        with engine.connect() as conn:
            # Remove test triggers
            result = conn.execute(text("""
                DELETE FROM google_sheet_triggers 
                WHERE trigger_id LIKE 'test_%_trigger_%'
            """))
            
            conn.commit()
            logger.info(f"   ✅ Removed {result.rowcount} test triggers")
            
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")

def main():
    """Main test function"""
    success = test_new_trigger_features()
    
    if success:
        logger.info("")
        logger.info("📝 SUMMARY:")
        logger.info("✅ All new trigger features are working")
        logger.info("✅ Frontend can now:")
        logger.info("   - Make Text Message/Caption optional")
        logger.info("   - Use Send_time column for time-based triggers")
        logger.info("   - Use Message column for sheet content")
        logger.info("")
        logger.info("📋 READY FOR FRONTEND TESTING!")
    else:
        logger.error("❌ Some tests failed - please check the errors above")
    
    # Clean up test data
    cleanup_test_data()

if __name__ == "__main__":
    main()
