try:
    from models.google_sheet import GoogleSheet, GoogleSheetTrigger
    print(f"GoogleSheet: {GoogleSheet}")
    print(f"GoogleSheetTrigger: {GoogleSheetTrigger}")
    print("Models imported successfully")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
