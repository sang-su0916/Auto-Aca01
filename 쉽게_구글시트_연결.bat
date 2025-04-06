@echo off
chcp 65001 > nul
title 구글 시트 간편 연결

echo ================================================
echo          구글 시트 간편 연결 도구
echo ================================================
echo.
echo 구글 시트 ID: 1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0
echo.

REM .env 파일 생성
echo GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 > .env
echo .env 파일이 생성되었습니다.

REM sheets 디렉토리 생성
if not exist sheets mkdir sheets
echo # Initialize sheets package > sheets\__init__.py
echo sheets 디렉토리가 생성되었습니다.

REM 필수 패키지 설치
echo.
echo 필수 패키지를 설치합니다...
pip install python-dotenv google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas streamlit

REM 환경 체크
echo.
echo 환경 설정 확인:
echo 1. credentials.json 파일이 있는지 확인하세요.
if exist credentials.json (
  echo   - credentials.json: 있음 (OK)
) else (
  echo   - credentials.json: 없음 (필요)
  echo     Google Cloud Console에서 서비스 계정 키를 다운로드하여 프로젝트 루트에 저장하세요.
)

echo 2. 구글 시트 공유 권한 설정:
echo   - https://docs.google.com/spreadsheets/d/1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 접속
echo   - '공유' 버튼 클릭
echo   - credentials.json 파일에 있는 client_email 값을 확인하여 '편집자' 권한으로 추가

echo.
echo 준비가 완료되었습니다!
echo.
echo 다음 명령으로 앱을 실행하세요:
echo streamlit run app.py
echo.
echo 계속하려면 아무 키나 누르세요...
pause > nul 