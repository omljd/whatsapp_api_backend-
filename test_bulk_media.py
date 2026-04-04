from fastapi.testclient import TestClient
from main import app
from api.auth import get_current_user
from models.busi_user import BusiUser
import json
import io
import uuid

def mock_get_current_user():
    user = BusiUser()
    user.busi_user_id = uuid.uuid4()
    user.email = "test@example.com"
    return user

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

def test_campaign_create_with_media():
    print("🚀 Testing campaign creation with media upload...")
    
    # 1. Prepare JSON Payload
    payload = {
        "name": "Test Media Campaign via TestClient",
        "sheet_id": str(uuid.uuid4()),
        "device_ids": [str(uuid.uuid4())],
        "templates": [
            {"content": "Hello this is a test with media!"}
        ]
    }
    
    # 2. Prepare mock file
    file_content = b"fake image content"
    file = io.BytesIO(file_content)
    file.name = "test_image.jpg"
    
    # Send request with multipart/form-data
    response = client.post(
        "/api/campaign/create",
        data={"payload": json.dumps(payload)},
        files={"file": ("test_image.jpg", file, "image/jpeg")}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print(f"Campaign ID: {data.get('id')}")
        print(f"Media URL: {data.get('media_url')}")
        print(f"Media Type: {data.get('media_type')}")
        
        if data.get('media_url') and data.get('media_type') == 'image':
            print("✅ Media fields are correctly populated in the response.")
        else:
            print("❌ Media fields are missing or incorrect.")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    test_campaign_create_with_media()
