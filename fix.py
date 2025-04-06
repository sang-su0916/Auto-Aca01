import os

# Create .env file
with open(".env", "w") as f:
    f.write("GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0\n")
print("Created .env file")

# Create sheets directory
if not os.path.exists("sheets"):
    os.makedirs("sheets")
    
# Create __init__.py file
with open("sheets/__init__.py", "w") as f:
    f.write("# Initialize sheets package\n")
print("Created sheets directory")

# Check credentials.json
if os.path.exists("credentials.json"):
    print("credentials.json exists")
else:
    print("WARNING: credentials.json not found!")

print("\nNow run these commands:")
print("pip install python-dotenv google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas streamlit")
print("streamlit run app.py") 