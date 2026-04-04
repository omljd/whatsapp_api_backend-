#!/usr/bin/env python3
"""
🧪 TEST SCRIPT: Google Sheet Manual Messaging

Tests both TEXT and TEMPLATE messages for the provided Google Sheet
Sheet ID: 1Cd-YVW119l4yAp3Q5ibnhRcDS0D80nrj8D239F2BUPo
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service import GoogleSheetsService
from services.official_message_service import OfficialMessageService
from services.whatsapp_session_service import WhatsAppSessionService
from models.official_whatsapp_config import OfficialWhatsAppConfig
from models.busi_user import BusiUser
from db.session import get_db, SessionLocal

# Test data from the provided Google Sheet
TEST_PHONE_NUMBERS = [
    "919145291501",  # jaypal
    "918767647149",  # sagar  
    "918378031442",  # vikas
    "917249086970",  # vikas_two
    "917887640770",  # new
]

TEST_SHEET_ID = "1Cd-YVW119l4yAp3Q5ibnhRcDS0D80nrj8D239F2BUPo"

async def test_google_sheet_connection():
    """Test 1: Connect to the Google Sheet"""
    print("🔗 TEST 1: Connecting to Google Sheet...")
    print(f"   Sheet ID: {TEST_SHEET_ID}")
    
    try:
        sheets_service = GoogleSheetsService()
        
        # Test fetching data from the sheet
        rows_data, headers = sheets_service.get_sheet_data_with_headers(
            credentials=None,
            spreadsheet_id=TEST_SHEET_ID,
            worksheet_name="Sheet1"
        )
        
        print(f"   ✅ SUCCESS: Found {len(rows_data)} rows with headers: {headers}")
        
        # Display the data
        print("\n   📊 SHEET DATA:")
        for i, row in enumerate(rows_data[:5]):  # Show first 5 rows
            print(f"   Row {i+1}: {row['data']}")
        
        return True, rows_data, headers
        
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        return False, None, None

async def test_session_validation():
    """Test 2: Validate 24-hour sessions for text messages"""
    print("\n🕒 TEST 2: 24-Hour Session Validation...")
    
    db = SessionLocal()
    try:
        session_service = WhatsAppSessionService(db)
        
        # Test each phone number
        results = []
        for phone in TEST_PHONE_NUMBERS:
            validation = session_service.validate_text_message_session("test_user", phone)
            results.append(validation)
            
            status = "✅ VALID" if validation["can_send_text"] else "❌ INVALID"
            reason = validation.get("reason", "unknown")
            hours = validation.get("hours_since_last_message", "N/A")
            
            print(f"   {phone}: {status} ({reason}) - {hours}h since last message")
        
        # Summary
        valid_count = sum(1 for r in results if r["can_send_text"])
        print(f"\n   📊 SUMMARY: {valid_count}/{len(TEST_PHONE_NUMBERS)} have valid sessions")
        
        return results
        
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        return None
    finally:
        db.close()

async def test_text_message_send():
    """Test 3: Send text messages (if sessions allow)"""
    print("\n📝 TEST 3: Text Message Sending...")
    
    db = SessionLocal()
    try:
        # Get a test user (you'll need to replace with actual user ID)
        test_user_id = "db6a2832-496d-4efa-922f-003b1a8f2b13"  # Replace with actual user ID
        
        message_service = OfficialMessageService(db)
        
        test_message = "Hello {{Name}}, this is a test message from Google Sheet automation!"
        
        results = []
        for i, phone in enumerate(TEST_PHONE_NUMBERS):
            print(f"   📤 Sending text to {phone}...")
            
            result = await message_service.send_official_text_message(
                user_id=test_user_id,
                phone_number=phone,
                message_text=test_message
            )
            
            results.append(result)
            
            if result["success"]:
                print(f"   ✅ SUCCESS: {result.get('message_id', 'No ID')}")
            else:
                print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
        
        # Summary
        success_count = sum(1 for r in results if r["success"])
        print(f"\n   📊 TEXT SUMMARY: {success_count}/{len(TEST_PHONE_NUMBERS)} sent successfully")
        
        return results
        
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        return None
    finally:
        db.close()

async def test_template_message_send():
    """Test 4: Send template messages"""
    print("\n📋 TEST 4: Template Message Sending...")
    
    db = SessionLocal()
    try:
        test_user_id = "db6a2832-496d-4efa-922f-003b1a8f2b13"  # Replace with actual user ID
        
        message_service = OfficialMessageService(db)
        
        # You'll need to replace with an actual approved template name
        template_name = "test_template"  # Replace with actual template name
        
        results = []
        for phone in TEST_PHONE_NUMBERS:
            print(f"   📤 Sending template to {phone}...")
            
            result = await message_service.send_official_template_message(
                user_id=test_user_id,
                phone_number=phone,
                template_name=template_name,
                language_code="en_US",
                header_params=[],
                body_params=["Test User", "Google Sheet Test"]
            )
            
            results.append(result)
            
            if result["success"]:
                print(f"   ✅ SUCCESS: {result.get('message_id', 'No ID')}")
            else:
                print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
        
        # Summary
        success_count = sum(1 for r in results if r["success"])
        print(f"\n   📊 TEMPLATE SUMMARY: {success_count}/{len(TEST_PHONE_NUMBERS)} sent successfully")
        
        return results
        
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        return None
    finally:
        db.close()

async def main():
    """Run all tests"""
    print("🧪 GOOGLE SHEET MESSAGING TEST SUITE")
    print("=" * 50)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Testing {len(TEST_PHONE_NUMBERS)} phone numbers")
    print("=" * 50)
    
    # Test 1: Google Sheet Connection
    sheet_success, rows_data, headers = await test_google_sheet_connection()
    
    if not sheet_success:
        print("\n❌ Cannot proceed without Google Sheet access")
        return
    
    # Test 2: Session Validation
    session_results = await test_session_validation()
    
    # Test 3: Text Messages (only if we have some valid sessions)
    if session_results and any(r["can_send_text"] for r in session_results):
        text_results = await test_text_message_send()
    else:
        print("\n⏭️  SKIPPING TEXT MESSAGES: No valid sessions found")
        text_results = None
    
    # Test 4: Template Messages
    template_results = await test_template_message_send()
    
    # Final Report
    print("\n" + "=" * 50)
    print("📋 FINAL TEST REPORT")
    print("=" * 50)
    
    print(f"📊 Google Sheet Access: {'✅ SUCCESS' if sheet_success else '❌ FAILED'}")
    print(f"🕒 Session Validation: {'✅ COMPLETED' if session_results else '❌ FAILED'}")
    print(f"📝 Text Messages: {'✅ TESTED' if text_results else '⏭️ SKIPPED'}")
    print(f"📋 Template Messages: {'✅ TESTED' if template_results else '❌ FAILED'}")
    
    if session_results:
        valid_sessions = sum(1 for r in session_results if r["can_send_text"])
        print(f"\n📊 SESSION BREAKDOWN:")
        print(f"   Valid Sessions: {valid_sessions}/{len(TEST_PHONE_NUMBERS)}")
        print(f"   Invalid Sessions: {len(TEST_PHONE_NUMBERS) - valid_sessions}/{len(TEST_PHONE_NUMBERS)}")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    if session_results and any(r["can_send_text"] for r in session_results):
        print("   ✅ Text messages can be sent to recipients with valid sessions")
    else:
        print("   ⚠️  Use template messages for all recipients (no session restrictions)")
    
    print("\n🏁 TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())
