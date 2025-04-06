@echo off
echo ================================================
echo          구글 시트 연동 문제 해결 도구
echo ================================================
echo.

echo 구글 시트 연동 문제를 해결합니다...
echo.

REM Python 환경 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요.
    pause
    exit /b
)

REM 필요한 패키지 설치
echo 필요한 패키지를 설치합니다...
pip install -r requirements.txt
pip install python-dotenv google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas

echo.
echo ------------------------------------------------
echo           구글 시트 연동 문제 해결 중
echo ------------------------------------------------
echo.

REM 구글 시트 연동 문제 해결 스크립트 실행
python fix_google_connection.py

echo.
echo ------------------------------------------------
echo          앱 시작 (문제 해결 확인)
echo ------------------------------------------------
echo.

REM 앱 실행 (사용자가 연동 문제 해결 확인할 수 있도록)
python app.py

echo.
pause 