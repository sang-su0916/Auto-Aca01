@echo off
chcp 65001 > nul
title 구글 시트 연동 빠른 해결

echo ================================================
echo          구글 시트 연동 빠른 해결
echo ================================================
echo.

REM 필수 패키지 직접 설치
echo 필수 패키지를 직접 설치합니다...

pip install --no-warn-script-location python-dotenv
pip install --no-warn-script-location google-auth 
pip install --no-warn-script-location google-auth-oauthlib
pip install --no-warn-script-location google-auth-httplib2
pip install --no-warn-script-location google-api-python-client
pip install --no-warn-script-location pandas
pip install --no-warn-script-location streamlit

REM .env 파일 생성
echo.
echo .env 파일을 생성합니다...
echo GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 > .env
echo .env 파일 생성 완료

REM sheets 디렉토리 설정
echo.
echo sheets 디렉토리를 설정합니다...
if not exist sheets mkdir sheets
echo # Initialize sheets package > sheets\__init__.py
echo sheets 디렉토리 설정 완료

echo.
echo ================================================
echo 모든 설정이 완료되었습니다!
echo.
echo 계속해서 앱을 실행하려면 다음 명령어를 직접 입력하세요:
echo.
echo streamlit run app.py
echo ================================================
echo.
echo 계속하려면 아무 키나 누르세요...
pause > nul 