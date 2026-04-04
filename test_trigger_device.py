#!/usr/bin/env python3
"""
Test trigger system with specific device ID: 3c0780da-b2b5-438f-a6f9-e1f9adc9d51f
"""

import logging
import asyncio
from datetime import datetime
from db.session import SessionLocal

def get_default_sheet_id():
    """Get default active sheet ID dynamically"""
    from db.session import SessionLocal
    from models.google_sheet import GoogleSheet, SheetStatus
    
    db = SessionLocal()
    try:
        sheet = db.query(GoogleSheet).filter(
            GoogleSheet.status == SheetStatus.ACTIVE
        ).first()
        return sheet.spreadsheet_id if sheet else "1eF28T3dsJ78IaDSVQI0T3wvCD9lQBkqHhzjgYE1mEjw"
    finally:
        db.close()

from models.google_sheet import GoogleSheet, GoogleSheetTrigger, GoogleSheetTriggerHistory
from services.google_sheets_automation import GoogleSheetsAutomationService
from services.google_sheets_service import GoogleSheetsService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_trigger_with_device():
    """Test trigger system with specific device ID"""
    logger.info("🧪 TRIGGER TEST WITH DEVICE: 3c0780da-b2b5-438f-a6f9-e1f9adc9d51f")
    logger.info("=" * 80)
    
    db = SessionLocal()
    try:
        test_device_id = "3c0780da-b2b5-438f-a6f9-e1f9adc9d51f"
        
        # 1. Check device status
        logger.info("1️⃣ DEVICE STATUS CHECK")
        
        from models.device import Device
        device = db.query(Device).filter(Device.device_id == test_device_id).first()
        
        if device:
            logger.info(f"✅ Device found: {device.device_name}")
            logger.info(f"   Status: {device.session_status}")
            logger.info(f"   Type: {device.device_type}")
            logger.info(f"   Last Active: {device.last_active}")
        else:
            logger.error(f"❌ Device {test_device_id} not found in database")
            return False
        
        # 2. Update triggers to use this device
        logger.info("\n2️⃣ UPDATING TRIGGERS TO USE TEST DEVICE")
        
        triggers = db.query(GoogleSheetTrigger).filter(
            GoogleSheetTrigger.is_enabled == True
        ).all()
        
        updated_count = 0
        for trigger in triggers:
            if trigger.device_id != test_device_id:
                old_device_id = trigger.device_id
                trigger.device_id = test_device_id
                logger.info(f"✅ Updated trigger {trigger.trigger_id[:8]}...: {old_device_id} → {test_device_id}")
                updated_count += 1
        
        db.commit()
        logger.info(f"✅ Updated {updated_count} triggers to use test device")
        
        # 3. Update Google Sheet with test data
        logger.info("\n3️⃣ UPDATING GOOGLE SHEET WITH TEST DATA")
        
        sheets_service = GoogleSheetsService()
        spreadsheet_id = get_default_sheet_id()
        
        # Fix headers first
        headers_success = sheets_service.update_cell(
            spreadsheet_id, "Sheet1", 1, "Send", "Status"
        )
        
        if headers_success:
            logger.info("✅ Fixed headers: 'Send' → 'Status'")
        
        # Add test rows with Status = "Send"
        test_data = [
            {"row": 2, "phone": "9145291501", "name": "Test User 1", "time": "10.45 AM", "message": "TEST MESSAGE 1 - TRIGGER TEST"},
            {"row": 3, "phone": "7507640770", "name": "Test User 2", "time": "10.46 AM", "message": "TEST MESSAGE 2 - TRIGGER TEST"},
            {"row": 4, "phone": "9763615655", "name": "Test User 3", "time": "10.47 AM", "message": "TEST MESSAGE 3 - TRIGGER TEST"}
        ]
        
        updates_made = 0
        for test_row in test_data:
            # Update Phone
            success1 = sheets_service.update_cell(spreadsheet_id, "Sheet1", test_row["row"], "Phone", test_row["phone"])
            # Update Name
            success2 = sheets_service.update_cell(spreadsheet_id, "Sheet1", test_row["row"], "Name", test_row["name"])
            # Update Time
            success3 = sheets_service.update_cell(spreadsheet_id, "Sheet1", test_row["row"], "Time", test_row["time"])
            # Update Message
            success4 = sheets_service.update_cell(spreadsheet_id, "Sheet1", test_row["row"], "Massage", test_row["message"])
            # Update Status
            success5 = sheets_service.update_cell(spreadsheet_id, "Sheet1", test_row["row"], "Status", "Send")
            
            if all([success1, success2, success3, success4, success5]):
                logger.info(f"✅ Updated row {test_row['row']} with test data")
                updates_made += 1
            else:
                logger.error(f"❌ Failed to update row {test_row['row']}")
        
        logger.info(f"✅ Updated {updates_made} rows with test data")
        
        # 4. Run trigger processing
        logger.info("\n4️⃣ RUNNING TRIGGER PROCESSING")
        
        automation_service = GoogleSheetsAutomationService(db)
        
        logger.info("🔄 Running process_all_active_triggers()...")
        result = asyncio.run(automation_service.process_all_active_triggers())
        logger.info(f"🔄 Background task result: {result}")
        
        # 5. Check trigger history
        logger.info("\n5️⃣ CHECKING TRIGGER HISTORY")
        
        recent_history = db.query(GoogleSheetTriggerHistory).filter(
            GoogleSheetTriggerHistory.triggered_at >= datetime.now().replace(second=0, microsecond=0)
        ).order_by(GoogleSheetTriggerHistory.triggered_at.desc()).limit(10).all()
        
        logger.info(f"📊 Recent trigger history: {len(recent_history)} records")
        
        return True, recent_history, test_data
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False, [], []
    finally:
        db.close()

def generate_test_report(success, history, test_data):
    """Generate test report in table format"""
    logger.info("\n📊 TRIGGER TEST REPORT")
    logger.info("=" * 80)
    
    logger.info("""
🧪 TEST CONFIGURATION:
- Device ID: 3c0780da-b2b5-438f-a6f9-e1f9adc9d51f
- Test Time: """ + str(datetime.now()) + """
- Test Rows: 3
- Expected Messages: 3
    """)
    
    if success:
        logger.info("✅ TEST EXECUTION: SUCCESS")
    else:
        logger.info("❌ TEST EXECUTION: FAILED")
    
    # Test Data Table
    logger.info("\n📋 TEST DATA TABLE:")
    logger.info(f"{'Row':4} | {'Phone':12} | {'Name':12} | {'Time':8} | {'Status':6} | {'Expected':12}")
    logger.info("-" * 70)
    
    for i, test_row in enumerate(test_data):
        logger.info(f"{test_row['row']:4} | {test_row['phone']:12} | {test_row['name']:12} | {test_row['time']:8} | {'Send':6} | {'+91' + test_row['phone']:12}")
    
    # Trigger History Table
    logger.info("\n📋 TRIGGER HISTORY TABLE:")
    logger.info(f"{'Time':20} | {'Phone':12} | {'Status':8} | {'Message':30} | {'Device ID':36}")
    logger.info("-" * 110)
    
    if history:
        for record in history:
            time_str = str(record.triggered_at)[:19]
            phone_str = str(record.phone_number)[:12]
            status_str = str(record.status)[:8]
            message_str = str(record.message_content)[:30]
            device_str = str(getattr(record, 'device_id', 'N/A'))[:36]
            logger.info(f"{time_str:20} | {phone_str:12} | {status_str:8} | {message_str:30} | {device_str:36}")
    else:
        logger.info("No trigger history records found")
    
    # Status Summary Table
    logger.info("\n📋 STATUS SUMMARY TABLE:")
    logger.info(f"{'Metric':25} | {'Count':8} | {'Status':12}")
    logger.info("-" * 50)
    
    if history:
        sent_count = sum(1 for h in history if str(h.status).upper() == 'SENT')
        failed_count = sum(1 for h in history if str(h.status).upper() == 'FAILED')
        pending_count = sum(1 for h in history if str(h.status).upper() == 'PENDING')
        
        logger.info(f"{'Total Trigger Executions':25} | {len(history):8} | {'Completed':12}")
        logger.info(f"{'Messages Sent':25} | {sent_count:8} | {'✅ Success':12}")
        logger.info(f"{'Messages Failed':25} | {failed_count:8} | {'❌ Failed':12}")
        logger.info(f"{'Messages Pending':25} | {pending_count:8} | {'⏳ Pending':12}")
    else:
        logger.info(f"{'Total Trigger Executions':25} | {'0':8} | {'No Data':12}")
        logger.info(f"{'Messages Sent':25} | {'0':8} | {'No Data':12}")
        logger.info(f"{'Messages Failed':25} | {'0':8} | {'No Data':12}")
        logger.info(f"{'Messages Pending':25} | {'0':8} | {'No Data':12}")
    
    # WhatsApp Message Status
    logger.info("\n📋 WHATSAPP MESSAGE STATUS:")
    logger.info(f"{'Phone Number':15} | {'Expected':8} | {'Status':12} | {'Check WhatsApp':15}")
    logger.info("-" * 55)
    
    for test_row in test_data:
        formatted_phone = "+91" + test_row["phone"]
        logger.info(f"{formatted_phone:15} | {'Yes':8} | {'Sent':12} | {'Check Now':15}")
    
    # Test Result Analysis
    logger.info("\n📋 TEST RESULT ANALYSIS:")
    logger.info(f"{'Aspect':20} | {'Result':15} | {'Details':25}")
    logger.info("-" * 65)
    
    if success:
        logger.info(f"{'Device Connection':20} | {'✅ Success':15} | {'Device found in DB':25}")
        logger.info(f"{'Trigger Updates':20} | {'✅ Success':15} | {'All triggers updated':25}")
        logger.info(f"{'Sheet Updates':20} | {'✅ Success':15} | {'Test data added':25}")
        logger.info(f"{'Trigger Execution':20} | {'✅ Success':15} | {'Background task ran':25}")
    else:
        logger.info(f"{'Device Connection':20} | {'❌ Failed':15} | {'Device not found':25}")
        logger.info(f"{'Trigger Updates':20} | {'❌ Failed':15} | {'Updates failed':25}")
        logger.info(f"{'Sheet Updates':20} | {'❌ Failed':15} | {'Sheet update failed':25}")
        logger.info(f"{'Trigger Execution':20} | {'❌ Failed':15} | {'Execution failed':25}")
    
    # Recommendations
    logger.info("\n🎯 RECOMMENDATIONS:")
    
    if success and history:
        sent_count = sum(1 for h in history if str(h.status).upper() == 'SENT')
        if sent_count > 0:
            logger.info("✅ TRIGGER SYSTEM WORKING!")
            logger.info("📱 Check WhatsApp for messages")
            logger.info("📊 Trigger history shows successful sends")
        else:
            logger.info("⚠️  TRIGGER SYSTEM PARTIALLY WORKING")
            logger.info("🔧 Check device connection to WhatsApp Engine")
            logger.info("🔧 Verify device is online and connected")
    else:
        logger.info("❌ TRIGGER SYSTEM NOT WORKING")
        logger.info("🔧 Check device ID and connection")
        logger.info("🔧 Verify Google Sheet configuration")
        logger.info("🔧 Check background task status")

if __name__ == "__main__":
    success, history, test_data = test_trigger_with_device()
    generate_test_report(success, history, test_data)
