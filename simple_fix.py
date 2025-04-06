import os
from pathlib import Path

# Main function
def main():
    print("Simple Google Sheets Connection Fix")
    
    # Create .env file
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write("GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0\n")
        print(".env file created")
    else:
        print(".env file exists")
    
    # Check credentials.json
    creds_file = Path('credentials.json')
    if not creds_file.exists():
        print("credentials.json not found")
    else:
        print("credentials.json exists")
    
    # Create sheets directory if needed
    sheets_dir = Path('sheets')
    if not sheets_dir.exists():
        sheets_dir.mkdir()
        with open(sheets_dir / "__init__.py", 'w') as f:
            f.write("# Initialize sheets package\n")
        print("sheets directory created")
    else:
        print("sheets directory exists")
        
    # Print instructions
    print("\nTo fix Google Sheets connection:")
    print("1. Ensure credentials.json is in the project root")
    print("2. Run: pip install python-dotenv google-api-python-client pandas")
    print("3. Share your Google Sheet with the service account email in credentials.json")
    print("4. Run your app with: streamlit run app.py")
    
if __name__ == "__main__":
    main() 