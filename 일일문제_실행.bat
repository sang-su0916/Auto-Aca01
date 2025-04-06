@echo off
echo "학원 자동 첨삭 시스템 - 일일 문제 연동 버전"
echo "====================================="
echo.

:: Python 설치 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python이 설치되어 있지 않습니다. 설치 후 다시 시도해주세요.
    echo https://www.python.org/downloads/ 에서 Python을 다운로드 할 수 있습니다.
    pause
    exit /b
)

:: 필요한 패키지 설치
echo 필요한 패키지를 설치합니다...
pip install -r requirements.txt > nul 2>&1

:: 스프레드시트 ID를 .env 파일에 저장
if not exist .env (
    echo GOOGLE_SHEETS_SPREADSHEET_ID=1YcKaHcjnx5-WypEpYbcfg04s8TIq280l-gi6iISF5NQ > .env
    echo .env 파일이 생성되었습니다.
)

:: 앱 실행
echo 앱을 시작합니다...
streamlit run app.py

pause 