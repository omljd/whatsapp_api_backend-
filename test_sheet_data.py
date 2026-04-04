import json
import os
import sys
from sqlalchemy.orm import Session
from db.db_session import SessionLocal
from services.google_sheets_service import GoogleSheetsService
from models.google_sheet import GoogleSheet

def test():
    db = SessionLocal()
    # Find the most recent sheet
    sheet = db.query(GoogleSheet).order_by(GoogleSheet.created_at.desc()).first()
    if not sheet:
        print("No sheets found in DB.")
        return

    print(f"Testing sheet: {sheet.sheet_name} ({sheet.spreadsheet_id})")
    
    service = GoogleSheetsService()
    creds = service.get_service_account_credentials()
    
    rows, headers = service.get_sheet_data_with_headers(
        spreadsheet_id=sheet.spreadsheet_id,
        worksheet_name=sheet.worksheet_name or "Sheet1",
        credentials=creds
    )
    
    print(f"Headers: {headers}")
    print(f"Number of rows: {len(rows)}")
    for i, row in enumerate(rows[:10]):
        print(f"Row {i+1}: {row}")

if __name__ == "__main__":
    test()
