@echo off
chcp 65001 > nul
title 구글 시트 연동 설정

echo ================================================
echo        구글 시트 연동 처음부터 다시 설정하기
echo ================================================

echo 필요한 모듈을 확인하고 설치합니다...
pip install python-dotenv pandas google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client streamlit

echo.
echo 구글 시트 연동을 설정합니다...
python setup_sheets_fresh.py

echo.
echo 설정이 완료되었습니다.
echo 계속하려면 아무 키나 누르세요...
pause > nul 