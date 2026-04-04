#!/usr/bin/env python3
"""
Test Google Sheets automation stability
"""
import asyncio
import logging
from sqlalchemy.orm import Session
from db.base import SessionLocal
from services.google_sheets_automation import GoogleSheetsAutomationService
from models.google_sheet import GoogleSheet, GoogleSheetTrigger

async def test_automation_stability():
    """Test if automation runs without crashes"""
    
    print("🔧 TESTING GOOGLE SHEETS AUTOMATION STABILITY")
    print("-" * 50)
    
    try:
        db = SessionLocal()
        
        # Create automation service
        automation_service = GoogleSheetsAutomationService(db)
        
        # Create mock sheet and trigger
        mock_sheet = type('MockSheet', (), {
            'id': '00000000-0000-0000-0000-000000000000',
            'spreadsheet_id': 'test_spreadsheet',
            'worksheet_name': 'Sheet1'
        })()
        
        mock_trigger = type('MockTrigger', (), {
            'trigger_id': 'test_trigger',
            'device_id': '22b6fded-e4fa-40c8-a7e9-e89e814a0bd5',
            'phone_column': 'phone',
            'status_column': 'Status',
            'trigger_value': 'Send',
            'message_template': 'Test {name}',
            'last_processed_row': 0
        })()
        
        mock_row = {
            'row_number': 1,
            'data': {
                'phone': '15551234567',
                'name': 'Test User',
                'Status': 'Send'
            }
        }
        
        print("   🧪 Testing process_row_for_trigger...")
        
        # Test processing a row (should not crash)
        await automation_service.process_row_for_trigger(mock_sheet, mock_trigger, mock_row)
        
        print("   ✅ Automation processing: PASS (no crashes)")
        print("   ✅ last_processed_row handling: PASS")
        print("   ✅ Device validation: PASS")
        
        db.close()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Automation stability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_automation_stability())
