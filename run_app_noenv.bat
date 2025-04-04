@echo off
echo 학원 자동 첨삭 시스템을 시작합니다...
echo.

:: Python 설치 확인
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python이 설치되어 있지 않습니다.
    echo Python을 설치한 후 다시 시도해주세요.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 필요한 패키지 확인 및 설치
echo 필요한 패키지를 확인합니다...
python -c "import streamlit" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Streamlit 패키지가 설치되어 있지 않습니다. 설치합니다...
    pip install streamlit
)

python -c "import google.auth" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Google API 패키지가 설치되어 있지 않습니다. 설치합니다...
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
)

echo.
echo 학원 자동 첨삭 시스템을 실행합니다...
echo 브라우저가 자동으로 열리지 않는 경우 http://localhost:8501 을 방문해주세요.
echo.
echo 종료하려면 이 창을 닫거나 Ctrl+C를 누르세요.
echo.

:: 앱 실행
python -m streamlit run app.py

pause 