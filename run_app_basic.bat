@echo off
echo 학원 자동 첨삭 시스템 (기본 버전)을 시작합니다...
echo 이 버전은 Google Sheets API를 사용하지 않습니다.
echo 데이터는 메모리에만 저장됩니다.
echo.

REM Python 확인
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 Python을 다운로드하여 설치해주세요.
    pause
    exit /b 1
)

REM 앱 실행
echo Python을 사용하여 앱을 실행합니다...
python -m streamlit run app_basic.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 앱 실행 중 오류가 발생했습니다.
    echo 필요한 패키지를 설치한 후 다시 시도해보세요.
    echo.
    echo python -m pip install streamlit pandas
    echo.
    python -m pip install streamlit pandas
    echo.
    echo 패키지 설치가 완료되었습니다. 다시 앱을 실행합니다...
    python -m streamlit run app_basic.py
)

pause 