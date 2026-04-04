import sys
sys.path.append('.')
from services.google_sheets_service import GoogleSheetsService

def test_direct_fetch():
    """Test fetching data directly from Google Sheets"""
    service = GoogleSheetsService()
    
    if not service.sdk_available:
        print('Google SDK not available')
        return
    
    try:
        sheet_id = '1xOY27h0MViQqlibeYhmMVqtNqgJMH_i6rMG233hJJ-M'
        print(f'Testing direct fetch from sheet: {sheet_id}')
        
        rows, headers = service.get_sheet_data_with_headers(sheet_id, 'Sheet1')
        print(f'Headers: {headers}')
        print(f'Number of rows: {len(rows)}')
        
        print('\nFirst 5 rows:')
        for i, row in enumerate(rows[:5]):
            print(f'Row {i+1}: {row}')
            
        # Test the format expected by frontend
        frontend_format = {
            "headers": headers,
            "rows": [r['data'] for r in rows]
        }
        
        print(f'\nFrontend format (first 3 rows):')
        print(f'Headers: {frontend_format["headers"]}')
        for i, row in enumerate(frontend_format["rows"][:3]):
            print(f'Row {i+1}: {row}')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_direct_fetch()
