import requests

print('=== Testing Reseller Analytics API ===')

try:
    # Test reseller analytics endpoint
    response = requests.get('http://localhost:8000/api/reseller-analytics/dashboard/62a65ac1-5864-469c-bf4e-fb92d5c3b8e4', timeout=10)
    print(f'Reseller analytics status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Business users under reseller: {len(data.get("business_users", []))}')
        
        if data.get('business_users'):
            for user in data['business_users']:
                print(f'  - {user.get("business_name", "Unknown")}: {user.get("credits_remaining", 0)} credits')
    else:
        print('No business users found')
        
except Exception as e:
    print(f'❌ Error: {e}')
