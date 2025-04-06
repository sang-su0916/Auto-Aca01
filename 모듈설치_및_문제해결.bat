@echo off
echo ================================================
echo        구글 시트 연동 모듈 설치 및 문제 해결
echo ================================================
echo.

echo 필요한 모듈을 설치하고 문제를 해결합니다...
echo.

REM Python 환경 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요.
    pause
    exit /b
)

echo 1. 필요한 패키지 설치 중...
pip install python-dotenv pandas google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client streamlit

echo.
echo 2. 누락된 모듈 문제 해결 중...
python fix_missing_modules.py

echo.
echo 3. 구글 시트 연동 문제 해결 중...
python fix_google_connection.py

echo.
echo 4. 앱 시작 (문제 해결 확인)...
python app.py

echo.
echo 작업이 완료되었습니다.
echo.
pause 