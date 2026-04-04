#!/usr/bin/env python3
"""
Test the fixed ManualSendRequest schema
"""

from pydantic import ValidationError
from schemas.google_sheet import ManualSendRequest
import json

def test_manual_send_schema_fix():
    """Test the fixed ManualSendRequest schema"""
    
    print('🧪 Testing Fixed ManualSendRequest Schema')
    print('=' * 60)
    
    # Test cases
    test_cases = [
        {
            'name': 'Frontend payload with phone_col (should work now)',
            'payload': {
                'device_id': '4337c1ea-29fe-4673-b7bd-0c4bffca4ec5',
                'message_template': 'Hello {name}',
                'phone_col': 'A',  # Frontend format
                'send_all': True
            }
        },
        {
            'name': 'Backend payload with phone_column (should still work)',
            'payload': {
                'device_id': '4337c1ea-29fe-4673-b7bd-0c4bffca4ec5',
                'message_template': 'Hello {name}',
                'phone_column': 'A',  # Backend format
                'send_all': True
            }
        },
        {
            'name': 'Both fields provided (should use phone_col)',
            'payload': {
                'device_id': '4337c1ea-29fe-4673-b7bd-0c4bffca4ec5',
                'message_template': 'Hello {name}',
                'phone_col': 'A',
                'phone_column': 'B',  # Should be ignored
                'send_all': True
            }
        },
        {
            'name': 'Missing phone_col (should fail)',
            'payload': {
                'device_id': '4337c1ea-29fe-4673-b7bd-0c4bffca4ec5',
                'message_template': 'Hello {name}',
                'send_all': True
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f'\n🧪 Test {i}: {test_case["name"]}')
        print(f'   Payload: {json.dumps(test_case["payload"], indent=4)}')
        
        try:
            request = ManualSendRequest(**test_case['payload'])
            print(f'   ✅ Schema validation PASSED')
            print(f'   Parsed phone_column: "{request.phone_column}"')
            
        except ValidationError as e:
            print(f'   ❌ Schema validation FAILED')
            print(f'   Error: {e}')
            
        except Exception as e:
            print(f'   ❌ Unexpected error: {e}')
    
    print('\n' + '=' * 60)
    print('📋 Schema Fix Test Complete')

if __name__ == '__main__':
    test_manual_send_schema_fix()
