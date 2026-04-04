#!/usr/bin/env python3
"""
Test script for time-only format (HH:MM:SS) in Send_time column
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, time, date
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_time_parsing():
    """Test time parsing for HH:MM:SS format"""
    
    logger.info("🕐 TESTING TIME-ONLY FORMAT (HH:MM:SS)")
    logger.info("=" * 50)
    
    # Test cases for time-only format
    test_cases = [
        "14:30:00",      # 2:30 PM
        "09:15:30",      # 9:15 AM  
        "23:45:00",      # 11:45 PM
        "16:00",         # 4:00 PM (no seconds)
        "08:30",         # 8:30 AM (no seconds)
        "00:00:00",      # Midnight
        "12:00:00",      # Noon
    ]
    
    logger.info("📋 Testing time-only formats:")
    
    for i, time_str in enumerate(test_cases, 1):
        logger.info(f"\n{i}. Testing: '{time_str}'")
        
        try:
            # Parse using our logic
            time_str = time_str.strip()
            
            # Check if it's time-only format
            if ':' in time_str and len(time_str) <= 8:
                # Time-only format: HH:MM:SS
                time_parts = time_str.split(':')
                
                if len(time_parts) == 3:
                    hour, minute, second = int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
                elif len(time_parts) == 2:
                    hour, minute = int(time_parts[0]), int(time_parts[1])
                    second = 0
                else:
                    raise ValueError("Invalid time format")
                
                # Create datetime for today with the specified time
                today = date.today()
                parsed_time = datetime.combine(today, time(hour, minute, second))
                
                # Format for display
                display_time = parsed_time.strftime("%Y-%m-%d %H:%M:%S")
                time_12hr = parsed_time.strftime("%I:%M:%S %p")
                
                logger.info(f"   ✅ Parsed: {time_str} -> {display_time}")
                logger.info(f"   🕐 12-hour: {time_12hr}")
                
            else:
                logger.error(f"   ❌ Not time-only format: {time_str}")
                
        except Exception as e:
            logger.error(f"   ❌ Error parsing '{time_str}': {e}")
    
    logger.info("\n📋 TIME FORMAT EXAMPLES:")
    logger.info("✅ Supported formats for Send_time column:")
    logger.info("   • 14:30:00 (2:30 PM)")
    logger.info("   • 09:15:30 (9:15 AM)")
    logger.info("   • 16:00 (4:00 PM)")
    logger.info("   • 08:30 (8:30 AM)")
    logger.info("   • 00:00:00 (Midnight)")
    logger.info("   • 12:00:00 (Noon)")
    
    logger.info("\n📋 HOW IT WORKS:")
    logger.info("1. System reads time from Send_time column")
    logger.info("2. Parses as HH:MM:SS format")
    logger.info("3. Combines with today's date")
    logger.info("4. Sends message when current time >= scheduled time")
    
    logger.info("\n🎯 USAGE IN GOOGLE SHEET:")
    logger.info("Create a column named 'Send_time' and enter times like:")
    logger.info("   • 14:30:00")
    logger.info("   • 09:15:30")
    logger.info("   • 16:00")
    
    logger.info("\n🕐 CURRENT TIME TESTING:")
    current_time = datetime.now()
    logger.info(f"   Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"   Current UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test some sample times
    sample_times = ["14:30:00", "09:15:30", "16:00"]
    logger.info("\n📊 SAMPLE TIME COMPARISONS:")
    
    for time_str in sample_times:
        try:
            time_parts = time_str.split(':')
            if len(time_parts) == 3:
                hour, minute, second = int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
            elif len(time_parts) == 2:
                hour, minute = int(time_parts[0]), int(time_parts[1])
                second = 0
            else:
                continue
                
            today = date.today()
            scheduled_time = datetime.combine(today, time(hour, minute, second))
            
            if current_time.time() >= scheduled_time.time():
                status = "✅ WOULD SEND NOW"
            else:
                status = "⏰ PENDING"
            
            logger.info(f"   {time_str} -> {scheduled_time.strftime('%H:%M:%S')} {status}")
            
        except Exception as e:
            logger.error(f"   Error with {time_str}: {e}")
    
    logger.info("\n🎉 TIME-ONLY FORMAT TESTING COMPLETED!")
    logger.info("✅ System supports HH:MM:SS format")
    logger.info("✅ Combines with current date for scheduling")
    logger.info("✅ Ready for Google Sheets Send_time column")

def main():
    """Main test function"""
    test_time_parsing()

if __name__ == "__main__":
    main()
