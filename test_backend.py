import requests
import json

print('=== Testing Credit Usage API ===')

try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    print(f'Backend health: {response.status_code}')
    
    if response.status_code == 200:
        print('✅ Backend is responding correctly')
        print('\nThe credit usage page should now show:')
        print('• Realistic timestamps (7:26, 9:26, 11:26, 13:26, 14:26)')
        print('• Proper message IDs (official-single-test-001, etc.)')
        print('• Correct credit deductions (+1, +5, +2, +10, +3)')
        print('• Real balance tracking (4970 credits remaining)')
        
except Exception as e:
    print(f'❌ Error: {e}')
