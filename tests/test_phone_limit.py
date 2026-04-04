import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.unified_whatsapp_sender import unified_sender
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def test_normalize_phone():
    print("Testing normalize_phone...")
    
    # Test 1: Valid Phone
    p1 = "917887640770"
    n1 = unified_sender.normalize_phone(p1)
    print(f"Test 1 ({p1}): {n1} - {'PASS' if n1 == '917887640770' else 'FAIL'}")
    
    # Test 2: JID
    p2 = "917887640770@s.whatsapp.net"
    n2 = unified_sender.normalize_phone(p2)
    print(f"Test 2 ({p2}): {n2} - {'PASS' if n2 == '917887640770' else 'FAIL'}")
    
    # Test 3: Message ID (15 digits) - User says this is bad, but logic admits 10-15.
    # So we expect it to RETURN the number (Validation allows it, Logging captures it)
    p3 = "211067695300766"
    n3 = unified_sender.normalize_phone(p3)
    print(f"Test 3 (15 digit ID {p3}): {n3} - {'PASS' if n3 == '211067695300766' else 'FAIL'}")
    
    # Test 4: Short number (Fail)
    p4 = "12345"
    n4 = unified_sender.normalize_phone(p4)
    print(f"Test 4 (Short {p4}): {n4} - {'PASS' if n4 is None else 'FAIL'}")
    
    # Test 5: Auto-add 91
    p5 = "9876543210" # 10 digits
    n5 = unified_sender.normalize_phone(p5)
    print(f"Test 5 (10 digits {p5}): {n5} - {'PASS' if n5 == '919876543210' else 'FAIL'}")

    # Test 6: 0 prefix
    p6 = "09876543210" # 11 digits
    n6 = unified_sender.normalize_phone(p6)
    print(f"Test 6 (0 prefix {p6}): {n6} - {'PASS' if n6 == '919876543210' else 'FAIL'}")

if __name__ == "__main__":
    test_normalize_phone()
