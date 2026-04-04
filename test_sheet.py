import sys
sys.path.append('.')
from services.google_sheets_service import GoogleSheetsService

def test_sheet_data():
    service = GoogleSheetsService()
    
    if not service.sdk_available:
        print('Google SDK not available - checking credentials...')
        import os
        print(f'Current directory: {os.getcwd()}')
        print(f'Credentials file exists: {os.path.exists("credentials/google-service-account.json")}')
        return
    
    print('Google SDK is available')
    
    try:
        # Test with the provided sheet ID
        sheet_id = '1xOY27h0MViQqlibeYhmMVqtNqgJMH_i6rMG233hJJ-M'
        print(f'Testing with sheet ID: {sheet_id}')
        
        rows, headers = service.get_sheet_data_with_headers(sheet_id, 'Sheet1')
        print(f'Headers: {headers}')
        print(f'Number of rows: {len(rows)}')
        
        if rows:
            print(f'Sample row: {rows[0]}')
            print(f'First 3 rows:')
            for i, row in enumerate(rows[:3]):
                print(f'  Row {i+1}: {row}')
        else:
            print('No rows found')
            
    except Exception as e:
        print(f'Error fetching data: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_sheet_data()
