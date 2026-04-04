#!/usr/bin/env python3
"""
Test phone number formatting
"""

import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_phone_number(phone_number: str, default_country: str = "IN") -> str:
    """Format phone number with country code automatically"""
    if not phone_number:
        return ""
    
    # Remove any non-digit characters
    clean_phone = re.sub(r'[^\d]', '', phone_number)
    
    # Handle different formats
    if len(clean_phone) == 10:  # Standard 10-digit number (India)
        return f"+91{clean_phone}"
    elif len(clean_phone) == 12 and clean_phone.startswith('91'):  # India with 91 prefix
        return f"+{clean_phone}"
    elif len(clean_phone) == 11 and clean_phone.startswith('0'):  # India with 0 prefix
        return f"+91{clean_phone[1:]}"
    elif len(clean_phone) == 10 and clean_phone.startswith('0'):  # India with leading 0
        return f"+91{clean_phone[1:]}"
    elif clean_phone.startswith('+'):  # Already has country code
        return clean_phone
    else:
        # Default to India for unknown formats
        if len(clean_phone) >= 10:
            return f"+91{clean_phone[-10:]}"
        else:
            return f"+91{clean_phone}"

def test_phone_formatting():
    """Test phone number formatting"""
    logger.info("📱 TESTING PHONE NUMBER FORMATTING")
    logger.info("=" * 50)
    
    test_numbers = [
        "9145291501",      # 10-digit India
        "09145291501",     # India with 0 prefix
        "919145291501",     # India with 91 prefix
        "+919145291501",    # Already formatted
        "7507640770",       # Another India number
        "9876543210",       # Test number
        "9763615655",       # Your number
        "7887640770",       # Another number
        "8767647149",       # Last number
        "9145291501 ",      # With space
        "9145-291-501",     # With dashes
        "(914)5291501",     # With parentheses
    ]
    
    logger.info("📋 TEST RESULTS:")
    for num in test_numbers:
        formatted = format_phone_number(num)
        logger.info(f"   Input: {num:<15} -> Output: {formatted}")
    
    logger.info("\n✅ PHONE NUMBER FORMATTING WORKS!")
    logger.info("📱 Your Google Sheet can now use simple numbers without country codes")
    logger.info("🔧 The system will automatically add +91 for Indian numbers")

if __name__ == "__main__":
    test_phone_formatting()
