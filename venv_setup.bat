@echo off
echo 가상환경 설정 및 구글 시트 연동 준비를 시작합니다...

REM 가상환경 생성
echo 가상환경을 생성합니다...
py -m venv sheets_venv

REM 가상환경 활성화
echo 가상환경을 활성화합니다...
call sheets_venv\Scripts\activate.bat

REM 필요한 패키지 설치
echo 필요한 패키지를 설치합니다...
pip install python-dotenv google-auth google-auth-httplib2 google-auth-oauthlib google-api-python-client streamlit pandas

REM .env 파일 생성
echo .env 파일을 생성합니다...
echo GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 > .env

REM sheets 디렉토리 및 __init__.py 확인
if not exist sheets mkdir sheets
if not exist sheets\__init__.py echo # Initialize sheets package > sheets\__init__.py

REM credentials.json 확인
if exist credentials.json (
    echo credentials.json 파일이 존재합니다.
) else (
    echo 경고: credentials.json 파일이 없습니다!
    echo Google API 콘솔에서 서비스 계정 키를 다운로드하여 credentials.json으로 저장해주세요.
    echo https://console.cloud.google.com/apis/credentials
)

echo 가상환경 설정이 완료되었습니다!
echo.
echo 앱을 실행하려면 다음 명령어를 입력하세요:
echo sheets_venv\Scripts\activate.bat ^&^& streamlit run app.py
echo.
echo 가상환경을 비활성화하려면 'deactivate' 명령어를 입력하세요.
pause 