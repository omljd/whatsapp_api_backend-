from db.session import SessionLocal
from services.device_service import DeviceService
from schemas.device import DeviceRegisterRequest, DeviceType
import uuid
import logging

# Configure logging to see the error/success messages
logging.basicConfig(level=logging.INFO)

def test_registration():
    db = SessionLocal()
    device_service = DeviceService(db)
    
    # This is the Reseller ID from the error log
    reseller_id = uuid.UUID("a6b02694-8e95-4c4e-9fce-841e7eb1b3f0")
    
    request = DeviceRegisterRequest(
        device_name="Vikas Test Device (Fix Verification)",
        device_type=DeviceType.WEB,
        user_id=reseller_id # The schema might expect user_id inside too
    )
    
    try:
        print(f"Attempting to register device for Reseller {reseller_id}...")
        device = device_service.register_device(reseller_id, request)
        print(f"✅ SUCCESS: Device registered with ID {device.device_id}")
        
        # Cleanup (soft delete)
        device_service.logout_device(str(device.device_id))
        print(f"✅ Cleanup: Device marked as logged_out/inactive.")
        
    except ValueError as e:
        print(f"❌ FAILED: {e}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_registration()
