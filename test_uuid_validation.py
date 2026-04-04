#!/usr/bin/env python3

import uuid
from schemas.unified import UnifiedMessageRequest, MessageType

def test_uuid_validation():
    """Test that UnifiedMessageRequest accepts UUID device_id"""
    
    print("Testing UnifiedMessageRequest UUID validation...")
    
    # Test 1: UUID object
    test_uuid = uuid.uuid4()
    print(f"\n1. Testing with UUID object: {test_uuid}")
    
    try:
        request1 = UnifiedMessageRequest(
            to="+1234567890",
            user_id="test-user-id",
            device_id=test_uuid,  # Pass UUID object
            message="Test message"
        )
        print(f"✅ Success! device_id: {request1.device_id} (type: {type(request1.device_id)})")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 2: String UUID
    uuid_string = str(test_uuid)
    print(f"\n2. Testing with string UUID: {uuid_string}")
    
    try:
        request2 = UnifiedMessageRequest(
            to="+1234567890",
            user_id="test-user-id",
            device_id=uuid_string,  # Pass string
            message="Test message"
        )
        print(f"✅ Success! device_id: {request2.device_id} (type: {type(request2.device_id)})")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: None device_id
    print(f"\n3. Testing with None device_id")
    
    try:
        request3 = UnifiedMessageRequest(
            to="+1234567890",
            user_id="test-user-id",
            device_id=None,  # Pass None
            message="Test message"
        )
        print(f"✅ Success! device_id: {request3.device_id} (type: {type(request3.device_id)})")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_uuid_validation()
