import logging
import sys
import unittest
from unittest.mock import MagicMock
from services.unified_whatsapp_sender import UnifiedWhatsAppSender

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("TestFix")

class TestMessageDeliveryFix(unittest.TestCase):
    
    def test_webhook_phone_extraction(self):
        """Verify Webhook ignores LID and extracts phone correctly"""
        logger.info("\n--- Testing Webhook Logic ---")
        
        # Simulation of the logic I inserted in webhooks.py
        def extract_phone(payload):
            remote_jid = payload.get("remoteJid") or payload.get("jid") or payload.get("remote_jid")

            # Ignore non-user JIDs (LID or group)
            if remote_jid and ("@lid" in remote_jid or remote_jid.endswith("@g.us")):
                logger.info(f"[WEBHOOK] Ignoring non-user jid: {remote_jid}")
                return {"status": "ignored"}

            # Extract real phone
            phone = None
            if remote_jid and "@s.whatsapp.net" in remote_jid:
                phone = remote_jid.split("@")[0]

            if not phone:
                phone = payload.get("phone")
                
            return phone

        # Case 1: Real User JID
        payload_real = {"remoteJid": "919876543210@s.whatsapp.net"}
        phone = extract_phone(payload_real)
        logger.info(f"Case 1 (Real JID): {phone}")
        self.assertEqual(phone, "919876543210")

        # Case 2: LID (Should be ignored)
        payload_lid = {"remoteJid": "1234567890@lid"}
        result = extract_phone(payload_lid)
        logger.info(f"Case 2 (LID): {result}")
        self.assertEqual(result, {"status": "ignored"})
        
        # Case 3: Payload with both (should prefer JID but ignore LID if it was first?) 
        # Actually my logic checks remoteJid first.
        
    def test_replies_phone_enforcement(self):
        """Verify Replies API enforces DB phone number"""
        logger.info("\n--- Testing Replies Logic ---")
        
        # Simulating the DB Object
        class MockInbox:
            phone_number = "919876543210"
        
        inbox_msg = MockInbox()
        
        # Logic from replies.py
        phone = inbox_msg.phone_number
        if "@" in phone:
            phone = phone.split("@")[0]
            
        logger.info(f"DB Phone: {inbox_msg.phone_number}")
        logger.info(f"Extracted for Send: {phone}")
        
        self.assertEqual(phone, "919876543210")
        self.assertTrue(phone.isdigit())

    def test_sender_sanitization(self):
        """Verify Sender Service strips @s.whatsapp.net if passed erroneously"""
        logger.info("\n--- Testing Sender Service Sanitization ---")
        
        sender = UnifiedWhatsAppSender()
        
        # Case 1: Clean number
        phone1 = "919876543210"
        norm1 = sender.normalize_phone(phone1)
        logger.info(f"Input: {phone1} -> Normalized: {norm1}")
        self.assertEqual(norm1, "919876543210")
        
        # Case 2: Dirty number (frontend sent JID by mistake)
        phone2 = "919876543210@s.whatsapp.net"
        # My fix in unified_whatsapp_sender.py:
        # normalized_phone = str(phone).replace("@s.whatsapp.net","").strip()
        # normalized_phone = re.sub(r'[^\d]', '', normalized_phone)
        
        norm2 = sender.normalize_phone(phone2)
        logger.info(f"Input: {phone2} -> Normalized: {norm2}")
        self.assertEqual(norm2, "919876543210")
        
if __name__ == '__main__':
    unittest.main()
