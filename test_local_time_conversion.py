import sys
sys.path.append('.')
from db.session import SessionLocal
from models.message_usage import MessageUsageCreditLog
from datetime import datetime
import pytz

db = SessionLocal()

print('=== Testing Local Time Conversion ===')

# Create a test message log with current UTC time
om_lunge_id = 'c83ca739-3e10-42ea-aaa0-be59640ce872'
now_utc = datetime.utcnow()

# Add a test log
test_log = MessageUsageCreditLog(
    usage_id=f'test-local-{datetime.now().strftime("%Y%m%d%H%M%S")}',
    busi_user_id=om_lunge_id,
    message_id='test-local-time-message',
    credits_deducted=1,
    balance_after=999,
    timestamp=now_utc
)

db.add(test_log)
db.commit()

# Get the log back
log = db.query(MessageUsageCreditLog).filter(
    MessageUsageCreditLog.usage_id == test_log.usage_id
).first()

if log:
    print(f'UTC Time: {log.timestamp}')
    print(f'ISO Format: {log.timestamp.isoformat()}')
    
    # Show what JavaScript will display
    utc_time = pytz.utc.localize(log.timestamp)
    india_time = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
    
    print(f'India Time: {india_time.strftime("%Y-%m-%d %I:%M %p")}')
    print(f'\nFrontend will show:')
    print(f'  Date: {india_time.strftime("%b %d, %Y")}')
    print(f'  Time: {india_time.strftime("%I:%M %p")}')

db.close()
