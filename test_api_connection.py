import requests
import json

# Test the API endpoint directly
API_URL = "http://127.0.0.1:8000/api"

def test_sheet_connection():
    """Test connecting the sheet first"""
    connect_data = {
        "sheet_name": "Test Vendor Sheet",
        "spreadsheet_id": "1xOY27h0MViQqlibeYhmMVqtNqgJMH_i6rMG233hJJ-M",
        "worksheet_name": "Sheet1"
    }
    
    try:
        # First connect the sheet
        response = requests.post(f"{API_URL}/google-sheets/connect", json=connect_data)
        print(f"Connect response status: {response.status_code}")
        print(f"Connect response: {response.json()}")
        
        if response.status_code == 200:
            sheet_data = response.json()
            sheet_id = sheet_data.get('id')
            
            if sheet_id:
                # Now try to fetch rows
                rows_response = requests.get(f"{API_URL}/google-sheets/{sheet_id}/rows")
                print(f"\nRows response status: {rows_response.status_code}")
                print(f"Rows response: {rows_response.json()}")
            else:
                print("No sheet ID in response")
        else:
            print("Failed to connect sheet")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sheet_connection()
