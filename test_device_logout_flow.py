#!/usr/bin/env python3
"""
Comprehensive test for the device logout flow
"""

import asyncio
import requests
import json
import time
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = "http://localhost:8000"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/whatsapp_platform")

class DeviceLogoutTester:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def setup_test_data(self):
        """Create test device with references"""
        print("🔧 Setting up test data...")
        
        with self.SessionLocal() as db:
            try:
                # First try to find an existing user
                result = db.execute(text("""
                    SELECT busi_user_id FROM businesses LIMIT 1
                """))
                existing_user = result.fetchone()
                
                if existing_user:
                    user_id = existing_user[0]
                    print(f"   Using existing user: {user_id}")
                else:
                    # Create test user if not exists (without parent reseller for simplicity)
                    result = db.execute(text("""
                        INSERT INTO businesses (
                            busi_user_id, role, status, parent_reseller_id, name, username, email, phone, password_hash, business_name, created_at
                        ) VALUES (
                            '550e8400-e29b-41d4-a716-446655440001', 'RESELLER', 'ACTIVE', '550e8400-e29b-41d4-a716-446655440001', 
                            'Test User', 'testuser_550e8400', 'test_550e8400@example.com', '+1234567890', 'dummy_hash', 'Test Business', NOW()
                        )
                        ON CONFLICT (busi_user_id) DO NOTHING
                    """))
                    user_id = '550e8400-e29b-41d4-a716-446655440001'
                    print(f"   Created new user: {user_id}")
                
                # Create test device
                device_id = '550e8400-e29b-41d4-a716-446655440002'
                result = db.execute(text("""
                    INSERT INTO devices (device_id, busi_user_id, device_name, device_type, session_status, created_at)
                    VALUES (:device_id, :user_id, 'Test Device', 'web', 'connected', NOW())
                    ON CONFLICT (device_id) DO NOTHING
                """), {"device_id": device_id, "user_id": user_id})
                
                # Create test inbox records (references)
                result = db.execute(text("""
                    INSERT INTO whatsapp_inbox (id, device_id, phone_number, incoming_message, incoming_time)
                    VALUES 
                        ('550e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440002', '+1234567890', 'Test message 1', NOW()),
                        ('550e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440002', '+1234567891', 'Test message 2', NOW())
                    ON CONFLICT (id) DO NOTHING
                """))
                
                db.commit()
                print("✅ Test data created successfully")
                return True
                
            except Exception as e:
                print(f"❌ Failed to setup test data: {str(e)}")
                db.rollback()
                return False
    
    def check_device_state(self, device_id):
        """Check current device state in database"""
        with self.SessionLocal() as db:
            try:
                result = db.execute(text("""
                    SELECT session_status, is_active, disconnected_at 
                    FROM devices 
                    WHERE device_id = :device_id
                """), {"device_id": device_id})
                
                row = result.fetchone()
                if row:
                    return {
                        "session_status": row[0],
                        "is_active": row[1],
                        "disconnected_at": row[2]
                    }
                return None
                
            except Exception as e:
                print(f"❌ Failed to check device state: {str(e)}")
                return None
    
    def check_references(self, device_id):
        """Check reference counts for device"""
        with self.SessionLocal() as db:
            try:
                inbox_count = db.execute(text("""
                    SELECT COUNT(*) FROM whatsapp_inbox WHERE device_id = :device_id
                """), {"device_id": device_id}).scalar()
                
                sheet_count = db.execute(text("""
                    SELECT COUNT(*) FROM google_sheets WHERE device_id = :device_id
                """), {"device_id": device_id}).scalar()
                
                trigger_count = db.execute(text("""
                    SELECT COUNT(*) FROM google_sheet_triggers WHERE device_id = :device_id
                """), {"device_id": device_id}).scalar()
                
                history_count = db.execute(text("""
                    SELECT COUNT(*) FROM sheet_trigger_history WHERE device_id = :device_id
                """), {"device_id": device_id}).scalar()
                
                return {
                    "inbox": inbox_count,
                    "sheets": sheet_count,
                    "triggers": trigger_count,
                    "history": history_count
                }
                
            except Exception as e:
                print(f"❌ Failed to check references: {str(e)}")
                return None
    
    def test_logout_api(self):
        """Test the logout API endpoint"""
        print("\n🧪 Testing Device Logout API...")
        
        device_id = "550e8400-e29b-41d4-a716-446655440002"
        
        # Check initial state
        print("📊 Checking initial device state...")
        initial_state = self.check_device_state(device_id)
        initial_refs = self.check_references(device_id)
        
        print(f"   Initial state: {initial_state}")
        print(f"   Initial references: {initial_refs}")
        
        # Test logout API
        print("📤 Sending logout request...")
        try:
            response = requests.delete(f"{BACKEND_URL}/api/devices/{device_id}")
            
            print(f"   Response status: {response.status_code}")
            print(f"   Response body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Logout successful: {result}")
                
                # Verify final state
                print("📊 Checking final device state...")
                final_state = self.check_device_state(device_id)
                final_refs = self.check_references(device_id)
                
                print(f"   Final state: {final_state}")
                print(f"   Final references: {final_refs}")
                
                # Verify expectations
                success = True
                
                if final_state["session_status"] != "logged_out":
                    print(f"❌ Expected session_status='logged_out', got '{final_state['session_status']}'")
                    success = False
                
                if final_state["is_active"] != False:
                    print(f"❌ Expected is_active=False, got {final_state['is_active']}")
                    success = False
                
                if final_state["disconnected_at"] is None:
                    print(f"❌ Expected disconnected_at to be set")
                    success = False
                
                # References should be preserved
                if final_refs != initial_refs:
                    print(f"❌ References changed unexpectedly: {initial_refs} -> {final_refs}")
                    success = False
                
                if success:
                    print("✅ All verifications passed!")
                    return True
                else:
                    print("❌ Some verifications failed")
                    return False
                    
            else:
                print(f"❌ Logout failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ API request failed: {str(e)}")
            return False
    
    def test_device_not_found(self):
        """Test logout with non-existent device"""
        print("\n🧪 Testing Device Not Found scenario...")
        
        fake_device_id = "550e8400-e29b-41d4-a716-446655449999"
        
        try:
            response = requests.delete(f"{BACKEND_URL}/api/devices/{fake_device_id}")
            
            print(f"   Response status: {response.status_code}")
            print(f"   Response body: {response.text}")
            
            if response.status_code == 404:
                result = response.json()
                error_detail = result.get("detail")
                if error_detail == "device_not_found":
                    print("✅ Correctly returned 404 for non-existent device")
                    return True
                else:
                    print(f"❌ Expected error='device_not_found', got {error_detail}")
                    return False
            else:
                print(f"❌ Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API request failed: {str(e)}")
            return False
    
    def test_safe_hard_delete(self):
        """Test hard delete when no references exist"""
        print("\n🧪 Testing Safe Hard Delete scenario...")
        
        # Create device without references
        clean_device_id = "550e8400-e29b-41d4-a716-446655440005"
        
        with self.SessionLocal() as db:
            try:
                # First delete if exists
                db.execute(text("DELETE FROM devices WHERE device_id = :device_id"), {"device_id": clean_device_id})
                db.commit()
                
                # Create clean device
                db.execute(text("""
                    INSERT INTO devices (device_id, busi_user_id, device_name, device_type, session_status, created_at)
                    VALUES (:device_id, '550e8400-e29b-41d4-a716-446655440001', 'Clean Device', 'web', 'connected', NOW())
                """), {"device_id": clean_device_id})
                db.commit()
                
                print(f"   Created clean device: {clean_device_id}")
                
                # Test logout
                response = requests.delete(f"{BACKEND_URL}/api/devices/{clean_device_id}")
                
                print(f"   Response status: {response.status_code}")
                print(f"   Response body: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "deleted":
                        print("✅ Device hard deleted successfully (no references)")
                        
                        # Verify device is gone
                        state = self.check_device_state(clean_device_id)
                        if state is None:
                            print("✅ Device completely removed from database")
                            return True
                        else:
                            print(f"❌ Device still exists: {state}")
                            return False
                    else:
                        print(f"❌ Expected status='deleted', got {result}")
                        return False
                else:
                    print(f"❌ Logout failed with status {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Test setup failed: {str(e)}")
                return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        with self.SessionLocal() as db:
            try:
                db.execute(text("DELETE FROM whatsapp_inbox WHERE device_id IN ('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440005')"))
                db.execute(text("DELETE FROM devices WHERE device_id IN ('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440005')"))
                db.commit()
                print("✅ Test data cleaned up")
                
            except Exception as e:
                print(f"❌ Cleanup failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Device Logout Flow Tests\n")
        
        results = []
        
        # Setup
        if not self.setup_test_data():
            return False
        
        try:
            # Test 1: Normal logout with references
            results.append(self.test_logout_api())
            
            # Test 2: Device not found
            results.append(self.test_device_not_found())
            
            # Test 3: Safe hard delete
            results.append(self.test_safe_hard_delete())
            
        finally:
            # Cleanup
            self.cleanup_test_data()
        
        # Summary
        print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
        
        if all(results):
            print("🎉 All tests passed! Device logout flow is working correctly.")
            return True
        else:
            print("❌ Some tests failed. Please check the implementation.")
            return False

if __name__ == "__main__":
    tester = DeviceLogoutTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
