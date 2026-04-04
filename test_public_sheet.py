import os
import sys
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logging.basicConfig(level=logging.INFO)

CREDENTIALS_FILE = "credentials/google-service-account.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def test_sheet(spreadsheet_id):
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"No creds at {CREDENTIALS_FILE}")
        return
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        print("Success! Sheet title:", spreadsheet.get('properties', {}).get('title'))
    except HttpError as e:
        print("HttpError:", e)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_sheet(sys.argv[1])
    else:
        # A known public sheet ID for testing (e.g. some random public sheet)
        # 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms is a Google example sheet
        test_sheet('1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms')
