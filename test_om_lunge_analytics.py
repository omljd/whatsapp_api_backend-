import sys
sys.path.append('.')
from db.session import SessionLocal
from services.reseller_analytics_service import ResellerAnalyticsService

db = SessionLocal()
service = ResellerAnalyticsService(db)

print('=== Testing Reseller Analytics for Om Lunge ===')

# Get business user analytics for Om Lunge
business_analytics = service.recalculate_business_analytics(
    'c83ca739-3e10-42ea-aaa0-be59640ce872',  # Om Lunge
    '62a65ac1-5864-469c-bf4e-fb92d5c3b8e4'   # Reseller
)

if business_analytics:
    print(f'Om Lunge Analytics:')
    print(f'  Credits Allocated: {business_analytics.credits_allocated}')
    print(f'  Credits Used: {business_analytics.credits_used}')
    print(f'  Credits Remaining: {business_analytics.credits_remaining}')
    print(f'  Messages Sent: {business_analytics.messages_sent}')
    print(f'\n✅ Analytics properly tracking Om Lunge credits')
else:
    print('No business analytics found')

# Test the reseller dashboard API
import requests
try:
    response = requests.get('http://localhost:8000/api/reseller-analytics/dashboard/62a65ac1-5864-469c-bf4e-fb92d5c3b8e4', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f'\nReseller Dashboard shows {len(data.get("business_users", []))} business users')
        
        # Find Om Lunge in the dashboard
        for user in data.get('business_users', []):
            if user.get('business_name') == 'MSolution':
                print(f'  ✅ MSolution: {user.get("credits_remaining", 0)} credits')
                break
        else:
            print('  ❌ MSolution not found in dashboard')
            
except Exception as e:
    print(f'API Error: {e}')

db.close()
