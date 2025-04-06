import json
import os
from pathlib import Path

# Get the service account email from credentials.json
def get_service_account_email():
    creds_file = Path('credentials.json')
    
    if not creds_file.exists():
        print("Error: credentials.json file not found")
        return None
    
    try:
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
            
        if 'client_email' in creds_data:
            email = creds_data['client_email']
            print(f"Service Account Email: {email}")
            print("\nShare your Google Sheet with this email address (grant Editor permission)")
            print("URL: https://docs.google.com/spreadsheets/d/1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0")
            return email
        else:
            print("Error: client_email not found in credentials.json")
            return None
    
    except json.JSONDecodeError:
        print("Error: credentials.json is not a valid JSON file")
        return None
    except Exception as e:
        print(f"Error reading credentials.json: {str(e)}")
        return None

if __name__ == "__main__":
    email = get_service_account_email() 