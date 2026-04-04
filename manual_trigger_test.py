#!/usr/bin/env python3
"""
Manual trigger test - create a trigger and test with real Google Sheet data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from datetime import datetime
import logging

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

def create_manual_test_trigger():
    """Create a manual test trigger for real testing"""
    
    logger.info("🧪 CREATING MANUAL TEST TRIGGER")
    logger.info("=" * 50)
    
    try:
        with engine.connect() as conn:
            
            # Get sheet and device info
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
            
            if not sheet or not device:
                logger.error("❌ No sheet or device found")
                return False
            
            # Create a simple time-based trigger (immediate)
            current_time = datetime.now().strftime("%H:%M:%S")
            trigger_id = f"manual_test_{int(datetime.now().timestamp())}"
            
            conn.execute(text("""
                INSERT INTO google_sheet_triggers (
                    trigger_id, sheet_id, device_id, trigger_type, is_enabled,
                    phone_column, status_column, send_time_column, message_column,
                    trigger_value, created_at
                ) VALUES (
                    :trigger_id, :sheet_id, :device_id, 'time', true,
                    'phone', 'Status', 'Send_time', 'Message',
                    'Send', :created_at
                )
            """), {
                'trigger_id': trigger_id,
                'sheet_id': sheet[0],
                'device_id': device[0],
                'created_at': datetime.utcnow()
            })
            
            conn.commit()
            
            logger.info("✅ Manual test trigger created!")
            logger.info(f"   Trigger ID: {trigger_id}")
            logger.info(f"   Sheet: {sheet[1]}")
            logger.info(f"   Device: {device[1]}")
            logger.info(f"   Time: {current_time}")
            
            # Show Google Sheet setup
            logger.info("\n📋 GOOGLE SHEET SETUP:")
            logger.info("Create columns in your Google Sheet:")
            logger.info("   | phone      | Status | Send_time | Message")
            logger.info("   |------------|--------|-----------|---------")
            logger.info(f"   | +1234567890| Send   | {current_time} | Hello from sheet!")
            
            logger.info("\n📱 HOW TO TEST:")
            logger.info("1. Add the row above to your Google Sheet")
            logger.info("2. Call API: POST /api/google-sheets/[sheet-id]/check-triggers")
            logger.info("3. Check WhatsApp for the message")
            logger.info("4. Check trigger history for status")
            
            logger.info("\n🎯 EXPECTED RESULT:")
            logger.info("✅ Message sent to +1234567890")
            logger.info("✅ Content: 'Hello from sheet!'")
            logger.info("✅ Sheet Status updated to 'Sent'")
            logger.info("✅ Trigger history shows 'Sent'")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

def show_trigger_status():
    """Show current trigger status"""
    
    logger.info("\n📊 CURRENT TRIGGER STATUS:")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    t.trigger_id,
                    t.trigger_type,
                    t.is_enabled,
                    s.sheet_name,
                    d.device_name,
                    d.session_status
                FROM google_sheet_triggers t
                JOIN google_sheets s ON t.sheet_id = s.id
                JOIN devices d ON t.device_id = d.device_id
                ORDER BY t.created_at DESC
                LIMIT 5
            """))
            
            triggers = result.fetchall()
            
            if not triggers:
                logger.info("   No triggers found")
                return
            
            logger.info("   Recent triggers:")
            for trigger in triggers:
                trigger_id, trigger_type, enabled, sheet_name, device_name, device_status = trigger
                status_icon = "✅" if enabled else "❌"
                device_icon = "🟢" if device_status == "connected" else "🔴"
                logger.info(f"   {status_icon} {trigger_id} ({trigger_type}) on {sheet_name}")
                logger.info(f"      📱 {device_name} {device_icon}")
            
    except Exception as e:
        logger.error(f"❌ Error checking status: {e}")

def main():
    """Main function"""
    logger.info("🧪 MANUAL TRIGGER TEST")
    logger.info("This will create a test trigger for real message sending")
    
    # Show current status
    show_trigger_status()
    
    # Create test trigger
    success = create_manual_test_trigger()
    
    if success:
        logger.info("\n🎉 READY FOR TESTING!")
        logger.info("Your system is now configured to send real messages")
        logger.info("Follow the Google Sheet setup instructions above")
    else:
        logger.error("❌ Failed to create test trigger")

if __name__ == "__main__":
    main()
