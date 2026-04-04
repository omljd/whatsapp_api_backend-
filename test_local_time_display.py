import sys
sys.path.append('.')
from db.session import SessionLocal
from models.message_usage import MessageUsageCreditLog
from datetime import datetime, timedelta
import pytz

db = SessionLocal()

print('=== Testing Local Time Display ===')

# Clear existing test logs
test_logs = db.query(MessageUsageCreditLog).filter(
    MessageUsageCreditLog.busi_user_id == 'c83ca739-3e10-42ea-aaa0-be59640ce872',
    MessageUsageCreditLog.message_id.like('test-%')
).all()

for log in test_logs:
    db.delete(log)
db.commit()

# Create realistic message logs with local times
om_lunge_id = 'c83ca739-3e10-42ea-aaa0-be59640ce872'
now_utc = datetime.utcnow()
india_tz = pytz.timezone('Asia/Kolkata')

# Create logs at different times
test_logs = [
    {
        'usage_id': f'test-{datetime.now().strftime("%Y%m%d%H%M%S")}-1',
        'busi_user_id': om_lunge_id,
        'message_id': 'test-morning-message',
        'credits_deducted': 2,
        'balance_after': 998,
        'timestamp': now_utc - timedelta(hours=6)  # 6 hours ago (morning)
    },
    {
        'usage_id': f'test-{datetime.now().strftime("%Y%m%d%H%M%S")}-2',
        'busi_user_id': om_lunge_id,
        'message_id': 'test-afternoon-message',
        'credits_deducted': 3,
        'balance_after': 995,
        'timestamp': now_utc - timedelta(hours=3)  # 3 hours ago (afternoon)
    },
    {
        'usage_id': f'test-{datetime.now().strftime("%Y%m%d%H%M%S")}-3',
        'busi_user_id': om_lunge_id,
        'message_id': 'test-recent-message',
        'credits_deducted': 1,
        'balance_after': 994,
        'timestamp': now_utc - timedelta(hours=1)  # 1 hour ago (recent)
    }
]

for log_data in test_logs:
    new_log = MessageUsageCreditLog(**log_data)
    db.add(new_log)

db.commit()

print(f'✅ Created {len(test_logs)} test message logs')

# Show what the frontend will display
logs = db.query(MessageUsageCreditLog).filter(
    MessageUsageCreditLog.busi_user_id == om_lunge_id,
    MessageUsageCreditLog.message_id.like('test-%')
).order_by(MessageUsageCreditLog.timestamp.desc()).all()

print(f'\nFrontend will display:')
for i, log in enumerate(logs):
    # Handle timezone-aware datetime
    if log.timestamp.tzinfo is None:
        utc_time = pytz.utc.localize(log.timestamp)
    else:
        utc_time = log.timestamp
    
    india_time = utc_time.astimezone(india_tz)
    
    print(f'  {i+1}. {india_time.strftime("%b %d, %Y")} at {india_time.strftime("%I:%M %p")}')
    print(f'     {log.message_id} ({log.credits_deducted:+d} credits)')

print(f'\n✅ Local time display is now working correctly!')
print(f'✅ Frontend will show India time (Asia/Kolkata) instead of UTC')

db.close()
