
import os
import json
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CREDENTIALS_FILE = "e:/whatsapp_platform_api/wh-api-backend-vikas/credentials/google-service-account.json"
SPREADSHEET_ID = "1fB6lbLA_5WQDN1Xl2ZElCqoAKclxL6y2o5MAm3Kl558"

def test_sheet_permissions():
    try:
        with open(CREDENTIALS_FILE, "r") as f:
            creds_info = json.load(f)
        
        creds = Credentials.from_service_account_info(
            creds_info, 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=creds)
        
        # Try to read metadata first
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        logger.info(f"Successfully read metadata. Spreadsheet title: {sheet_metadata.get('properties', {}).get('title')}")
        
        # Try to write a test value to cell Z100 (unlikely to be used)
        range_name = 'Sheet1!Z100'
        body = {'values': [['PERMISSION_TEST']]}
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        
        logger.info(f"Successfully wrote to sheet! Updated cells: {result.get('updatedCells')}")
        return True
    except Exception as e:
        logger.error(f"Permission test failed: {e}")
        return False

if __name__ == "__main__":
    test_sheet_permissions()
