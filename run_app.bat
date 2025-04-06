@echo off
echo 학원 자동 첨삭 시스템을 실행합니다...

REM 환경 변수 파일 생성
echo GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 > .env

REM 가상환경 활성화
call sheets_venv\Scripts\activate.bat

REM 필요한 패키지 확인 및 설치
pip install -r requirements.txt

REM 인증 파일 확인
echo 인증 파일 확인 중...
if not exist credentials.json (
  echo 인증 파일이 없습니다. 새로 생성합니다.
  python sheets/setup_sheets.py
)

REM 앱 실행
echo 앱을 실행합니다...
streamlit run app.py

REM 스크립트 종료 시 가상환경 비활성화
call deactivate
pause 