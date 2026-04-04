
from db.session import SessionLocal
from services.campaign_service import CampaignService
from schemas.campaign import CampaignCreateRequest, MessageTemplateCreate
from models.device import Device
from models.google_sheet import GoogleSheet
import uuid

def test_campaign_creation():
    db = SessionLocal()
    try:
        # Get a valid user_id and device_id
        device = db.query(Device).filter(Device.is_active == True).first()
        if not device:
            print("No active devices found for testing.")
            return

        sheet = db.query(GoogleSheet).first()
        if not sheet:
            print("No google sheets found for testing.")
            return

        user_id = str(device.busi_user_id)
        
        # Mock request data
        request_data = CampaignCreateRequest(
            sheet_id=sheet.id,
            name="Test Media Campaign",
            device_ids=[device.device_id],
            templates=[
                MessageTemplateCreate(
                    content="Hello with image",
                    media_url="https://example.com/image.jpg",
                    media_type="image"
                )
            ]
        )
        
        service = CampaignService(db)
        campaign = service.create_campaign(user_id, request_data)
        
        print(f"Campaign created: {campaign.id}")
        print(f"Template count: {len(campaign.templates)}")
        for t in campaign.templates:
            print(f"Template Media URL: {t.media_url}")
            print(f"Template Media Type: {t.media_type}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_campaign_creation()
