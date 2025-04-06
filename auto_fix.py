"""
Google Sheets Connection Fix
Simple script to fix Google Sheets connection issues
"""

import os
import sys

def main():
    print("Google Sheets Connection Fix")
    
    # Create .env file
    print("Creating .env file...")
    with open(".env", "w") as f:
        f.write("GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0\n")
    print("Done")
    
    # Create sheets directory
    print("Creating sheets directory...")
    if not os.path.exists("sheets"):
        os.makedirs("sheets")
    
    # Create __init__.py file
    with open("sheets/__init__.py", "w") as f:
        f.write("# Initialize sheets package\n")
    print("Done")
    
    # Check credentials.json
    print("Checking credentials.json...")
    if os.path.exists("credentials.json"):
        print("credentials.json exists")
    else:
        print("WARNING: credentials.json not found!")
        print("Download service account key from Google Cloud Console")
    
    # Print next steps
    print("\nNext steps:")
    print("1. Run: pip install python-dotenv google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas streamlit")
    print("2. Share your Google Sheet with the service account email in credentials.json")
    print("3. Run your app with: streamlit run app.py")

if __name__ == "__main__":
    main() 