@echo off
chcp 65001 > nul
title 구글 시트 연동 - 기존 ID 설정

echo ================================================
echo        구글 시트 연동 - 기존 ID 설정
echo ================================================
echo.
echo 구글 시트 ID: 1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0
echo.

echo 필요한 모듈을 확인하고 설치합니다...
pip install python-dotenv pandas google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client streamlit

echo.
echo 구글 시트 ID로 연동을 설정합니다...
python app_sheets_update.py

echo.
echo 설정이 완료되었습니다. 테스트를 실행합니다...
python test_google_sheets.py

echo.
echo 계속하려면 아무 키나 누르세요...
pause > nul 