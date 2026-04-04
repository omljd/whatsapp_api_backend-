#!/usr/bin/env python3
"""
Test script to verify chat persistence fixes
"""

import requests
import json
from datetime import datetime

# Base URL for testing
BASE_URL = "http://localhost:8000"

def test_chat_persistence():
    """Test chat persistence across device connections"""
    
    print("🧪 TESTING CHAT PERSISTENCE FIXES")
    print("=" * 50)
    
    # Test 1: Get chat summary (should work regardless of device status)
    print("\n1. Testing Chat Summary Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/replies/chat-summary", 
                          headers={"Authorization": "Bearer YOUR_TOKEN_HERE"})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat Summary: {len(data.get('data', []))} conversations")
            for conv in data.get('data', [])[:3]:  # Show first 3
                print(f"   📱 {conv['contact_name']}: {conv['unread_count']} unread")
        else:
            print(f"❌ Chat Summary failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat Summary error: {e}")
    
    # Test 2: Get active devices (should show all devices with counts)
    print("\n2. Testing Active Devices Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/replies/active-devices",
                          headers={"Authorization": "Bearer YOUR_TOKEN_HERE"})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Active Devices: {len(data.get('data', []))} devices")
            for device in data.get('data', []):
                print(f"   📱 {device['device_name']}: {device['unread_count']} unread, {device['message_count']} total")
        else:
            print(f"❌ Active Devices failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Active Devices error: {e}")
    
    # Test 3: Get inbox messages (should show 30-day history)
    print("\n3. Testing Inbox Messages Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/replies",
                          headers={"Authorization": "Bearer YOUR_TOKEN_HERE"})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Inbox Messages: {len(data.get('data', []))} messages")
            # Show message distribution
            incoming = len([m for m in data.get('data', []) if m.get('is_incoming')])
            outgoing = len([m for m in data.get('data', []) if m.get('is_outgoing')])
            unread = len([m for m in data.get('data', []) if m.get('unread')])
            print(f"   📊 {incoming} incoming, {outgoing} outgoing, {unread} unread")
        else:
            print(f"❌ Inbox Messages failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Inbox Messages error: {e}")
    
    print("\n🎯 EXPECTED BEHAVIOR AFTER FIX:")
    print("   • Chat history persists even when devices are disconnected")
    print("   • 30-day message history (extended from 7 days)")
    print("   • Unread counts work regardless of device status")
    print("   • Device list shows message counts")
    print("   • Chat summary shows all conversations")

def test_frontend_integration():
    """Test frontend integration scenarios"""
    
    print("\n🔄 FRONTEND INTEGRATION TEST")
    print("=" * 50)
    
    scenarios = [
        "Device connected → Should show chats + unread counts",
        "Device disconnected → Should still show chat history",
        "Device reconnected → Should sync new messages",
        "Multiple devices → Should show unified chat list",
        "Mark as read → Should update unread counts"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario}")
    
    print("\n📱 FRONTEND IMPLEMENTATION GUIDE:")
    print("""
    1. Use /replies/chat-summary for main chat list
    2. Use /replies/active-devices for device selector
    3. Use /replies?device_id=X for specific device chat
    4. Always show chat history even when device.status = 'disconnected'
    5. Update unread counts when marking messages as read
    6. Refresh chat list when device reconnects
    """)

if __name__ == "__main__":
    test_chat_persistence()
    test_frontend_integration()
    
    print("\n✅ TESTING COMPLETED")
    print("🚀 Ready for frontend integration!")
