@echo off
title Quick Fix for Google Sheets

echo Creating .env file...
echo GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 > .env
echo Done.

echo Creating sheets directory...
if not exist sheets mkdir sheets
echo # Initialize sheets package > sheets\__init__.py
echo Done.

echo Installing required packages...
call pip install python-dotenv
call pip install google-auth
call pip install google-auth-oauthlib
call pip install google-auth-httplib2
call pip install google-api-python-client
call pip install pandas
call pip install streamlit
echo Done.

echo Checking credentials.json...
if exist credentials.json (
  echo credentials.json found.
) else (
  echo WARNING: credentials.json not found!
  echo Please download service account key from Google Cloud Console.
)

echo.
echo Setup complete! 
echo.
echo To run the app:
echo streamlit run app.py
echo.
pause 