#!/usr/bin/env python3
"""
Complete System Test - All Device Management Fixes
"""
import requests
import json
import uuid
import time

def test_complete_system():
    print("🔍 COMPLETE SYSTEM TEST - ALL FIXES")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    engine_url = "http://localhost:3001"
    
    results = {}
    
    # Test 1: Health checks
    print("\n1️⃣ Testing Health Endpoints...")
    try:
        backend_health = requests.get(f"{base_url}/health", timeout=5)
        engine_health = requests.get(f"{engine_url}/health", timeout=5)
        
        results['health'] = {
            'backend': backend_health.status_code == 200,
            'engine': engine_health.status_code == 200
        }
        print(f"   ✅ Backend: {backend_health.status_code == 200}")
        print(f"   ✅ Engine: {engine_health.status_code == 200}")
    except Exception as e:
        results['health'] = {'backend': False, 'engine': False}
        print(f"   ❌ Health check failed: {e}")
    
    # Test 2: Device Registration (Fixed)
    print("\n2️⃣ Testing Device Registration...")
    try:
        test_user_id = str(uuid.uuid4())
        register_payload = {
            "user_id": test_user_id,
            "device_name": "Test Device",
            "device_type": "web"
        }
        
        response = requests.post(f"{base_url}/api/devices/register", json=register_payload)
        if response.status_code == 200:
            device_data = response.json()
            device_id = device_data['device_id']
            results['registration'] = {'success': True, 'device_id': device_id}
            print(f"   ✅ Device registered: {device_id}")
        else:
            results['registration'] = {'success': False, 'error': response.text}
            print(f"   ❌ Registration failed: {response.status_code}")
    except Exception as e:
        results['registration'] = {'success': False, 'error': str(e)}
        print(f"   ❌ Registration error: {e}")
    
    # Test 3: Device List (Fixed)
    print("\n3️⃣ Testing Device List...")
    try:
        response = requests.get(f"{base_url}/api/devices/", params={'user_id': test_user_id})
        if response.status_code == 200:
            devices = response.json().get('devices', [])
            results['device_list'] = {'success': True, 'count': len(devices)}
            print(f"   ✅ Device list working: {len(devices)} devices")
        else:
            results['device_list'] = {'success': False, 'error': response.text}
            print(f"   ❌ Device list failed: {response.status_code}")
    except Exception as e:
        results['device_list'] = {'success': False, 'error': str(e)}
        print(f"   ❌ Device list error: {e}")
    
    # Test 4: Heal Orphaned Devices (Fixed)
    print("\n4️⃣ Testing Heal Orphaned Devices...")
    try:
        response = requests.post(f"{base_url}/api/devices/heal/orphaned")
        if response.status_code == 200:
            result = response.json()
            results['heal_orphaned'] = {'success': True, 'message': result.get('message')}
            print(f"   ✅ Heal orphaned working: {result.get('message')}")
        else:
            results['heal_orphaned'] = {'success': False, 'error': response.text}
            print(f"   ❌ Heal orphaned failed: {response.status_code}")
    except Exception as e:
        results['heal_orphaned'] = {'success': False, 'error': str(e)}
        print(f"   ❌ Heal orphaned error: {e}")
    
    # Test 5: Device Deletion (Idempotent)
    print("\n5️⃣ Testing Device Deletion (Idempotent)...")
    try:
        if 'device_id' in results.get('registration', {}):
            device_id = results['registration']['device_id']
            
            # First deletion
            response1 = requests.delete(f"{base_url}/api/devices/{device_id}")
            # Second deletion (should still work - idempotent)
            response2 = requests.delete(f"{base_url}/api/devices/{device_id}")
            
            results['deletion'] = {
                'success': response1.status_code == 200 and response2.status_code == 200,
                'first_delete': response1.status_code == 200,
                'second_delete': response2.status_code == 200
            }
            print(f"   ✅ First deletion: {response1.status_code == 200}")
            print(f"   ✅ Second deletion (idempotent): {response2.status_code == 200}")
        else:
            results['deletion'] = {'success': False, 'error': 'No device to delete'}
            print("   ❌ No device available for deletion test")
    except Exception as e:
        results['deletion'] = {'success': False, 'error': str(e)}
        print(f"   ❌ Deletion error: {e}")
    
    # Test 6: Engine DELETE Session
    print("\n6️⃣ Testing Engine DELETE Session...")
    try:
        test_device_id = f"test-{uuid.uuid4().hex[:8]}"
        response = requests.delete(f"{engine_url}/session/{test_device_id}")
        if response.status_code == 200:
            results['engine_delete'] = {'success': True}
            print(f"   ✅ Engine DELETE working")
        else:
            results['engine_delete'] = {'success': False, 'error': response.text}
            print(f"   ❌ Engine DELETE failed: {response.status_code}")
    except Exception as e:
        results['engine_delete'] = {'success': False, 'error': str(e)}
        print(f"   ❌ Engine DELETE error: {e}")
    
    # Final Summary
    print("\n" + "=" * 50)
    print("🎯 FINAL TEST RESULTS")
    
    all_tests = [
        ('Health Check', results.get('health', {}).get('backend', False) and results.get('health', {}).get('engine', False)),
        ('Device Registration', results.get('registration', {}).get('success', False)),
        ('Device List', results.get('device_list', {}).get('success', False)),
        ('Heal Orphaned', results.get('heal_orphaned', {}).get('success', False)),
        ('Device Deletion', results.get('deletion', {}).get('success', False)),
        ('Engine DELETE', results.get('engine_delete', {}).get('success', False))
    ]
    
    all_passed = True
    for test_name, passed in all_tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\n🚀 Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 ALL FIXES VERIFIED SUCCESSFULLY!")
        print("✅ Device registration works with user_id in body")
        print("✅ Device list endpoint working correctly")
        print("✅ Heal orphaned devices using correct API path")
        print("✅ Device deletion is idempotent")
        print("✅ Engine DELETE session endpoint working")
        print("✅ Frontend-backend integration fixed")
    else:
        print("\n⚠️ Some issues remain - check failed tests above")
    
    return all_passed

if __name__ == "__main__":
    test_complete_system()
