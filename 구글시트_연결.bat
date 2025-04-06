@echo off
echo ================================================
echo          학원 자동 첨삭 시스템 - 구글 시트 연결
echo ================================================
echo.

echo 구글 시트 연결 작업을 시작합니다...
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

echo.
echo ------------------------------------------------
echo           Google 스프레드시트 연결 중
echo ------------------------------------------------
echo.

REM 구글 시트 연결 및 초기화
python setup_and_connect.py

echo.
echo 작업이 완료되었습니다.
echo.
echo 구글 시트를 사용하기 위해 다음 단계를 따라주세요:
echo 1. 구글 스프레드시트를 열고 공유 설정에서 credentials.json 파일에 있는 
echo    서비스 계정 이메일에 편집 권한을 부여했는지 확인하세요.
echo 2. 앱을 실행하고 '문제 새로고침' 버튼을 클릭하여 연결을 확인하세요.
echo.

pause 