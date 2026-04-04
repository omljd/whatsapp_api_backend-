import sys
sys.path.append('.')
from db.session import SessionLocal
from models.busi_user import BusiUser
import jwt
from datetime import datetime, timedelta
import requests

db = SessionLocal()

print('=== Testing Token Generation ===')

# Get Om Lunge's account
om_lunge = db.query(BusiUser).filter(BusiUser.email == 'lungeom39@gmail.com').first()
if om_lunge:
    print(f'Found user: {om_lunge.business_name}')
    print(f'User ID: {om_lunge.busi_user_id}')
    
    # Create a test token (similar to what frontend would use)
    payload = {
        'sub': str(om_lunge.busi_user_id),
        'email': om_lunge.email,
        'role': 'business_user',
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    
    # Test token (using same secret as backend)
    test_token = jwt.encode(payload, 'your-super-secret-key-here-change-in-production', algorithm='HS256')
    print(f'Test token: {test_token[:50]}...')
    
    # Test the balance API with this token
    headers = {'Authorization': f'Bearer {test_token}'}
    response = requests.get('http://localhost:8000/api/v1/credits/balance', headers=headers, timeout=10)
    
    print(f'API Response Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Balance Data: {data}')
        print(f'Current Balance: {data.get("current_balance", "N/A")}')
    else:
        print(f'Error: {response.text}')

db.close()
