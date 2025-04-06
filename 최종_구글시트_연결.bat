@echo off
chcp 65001 > nul
title 최종 구글 시트 연결 도구

echo ================================================
echo          최종 구글 시트 연결 도구
echo ================================================
echo.
echo 구글 시트 ID: 1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0
echo.

REM 메뉴 표시
:menu
echo 작업을 선택하세요:
echo.
echo [1] 전체 설정 (환경 설정 + 모듈 설치)
echo [2] 앱 실행하기
echo [0] 종료
echo.
set /p choice=선택 (0-2): 

if "%choice%"=="1" goto all_settings
if "%choice%"=="2" goto run_app
if "%choice%"=="0" goto end

echo 잘못된 선택입니다. 다시 시도하세요.
goto menu

REM 전체 설정
:all_settings
echo.
echo ===== 전체 설정을 시작합니다 =====
echo.

REM 1. 환경 변수 파일 생성
echo 1단계: 환경 변수 파일 생성
echo GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 > .env
echo ✓ .env 파일 생성 완료

REM 2. sheets 디렉토리 생성
echo 2단계: sheets 디렉토리 생성
if not exist sheets mkdir sheets
echo # Initialize sheets package > sheets\__init__.py
echo ✓ sheets 디렉토리 설정 완료

REM 3. 필수 패키지 설치
echo 3단계: 필수 패키지 설치
echo 이 과정은 몇 분 정도 소요될 수 있습니다...
echo.

call pip install --no-warn-script-location python-dotenv
call pip install --no-warn-script-location google-auth 
call pip install --no-warn-script-location google-auth-oauthlib
call pip install --no-warn-script-location google-auth-httplib2
call pip install --no-warn-script-location google-api-python-client
call pip install --no-warn-script-location pandas
call pip install --no-warn-script-location streamlit

echo ✓ 모든 패키지 설치 완료

REM 4. 인증 파일 확인
echo 4단계: 인증 파일 확인
if exist credentials.json (
  echo ✓ credentials.json 파일이 확인되었습니다.
  
  REM 5. 서비스 계정 이메일 확인
  echo 5단계: 서비스 계정 이메일 확인
  echo import json > temp_email.py
  echo try: >> temp_email.py
  echo     with open('credentials.json', 'r') as f: >> temp_email.py
  echo         data = json.load(f) >> temp_email.py
  echo     if 'client_email' in data: >> temp_email.py
  echo         print("서비스 계정 이메일:", data['client_email']) >> temp_email.py
  echo     else: >> temp_email.py
  echo         print("오류: client_email을 찾을 수 없습니다") >> temp_email.py
  echo except Exception as e: >> temp_email.py
  echo     print("오류:", str(e)) >> temp_email.py
  
  python temp_email.py
  del temp_email.py
  
  echo.
  echo ================================================
  echo 위 이메일을 구글 시트에 '편집자'로 추가하세요:
  echo 1. 구글 시트 접속: https://docs.google.com/spreadsheets/d/1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0
  echo 2. '공유' 버튼 클릭
  echo 3. 위 이메일 주소 입력
  echo 4. '편집자' 권한 선택 후 '완료' 클릭
  echo ================================================
  echo.
) else (
  echo ✗ credentials.json 파일이 없습니다!
  echo Google Cloud Console에서 서비스 계정 키를 다운로드하여 이 폴더에 저장하세요.
  echo https://console.cloud.google.com/iam-admin/serviceaccounts
  echo.
)

echo 설정이 완료되었습니다!
echo 계속해서 앱을 실행하시겠습니까? (Y/N)
set /p run_choice=선택: 
if /i "%run_choice%"=="Y" goto run_app

echo.
echo 메인 메뉴로 돌아갑니다.
pause
goto menu

REM 앱 실행
:run_app
echo.
echo ===== 앱 실행을 준비합니다 =====

REM 필요한 파일 재확인
if not exist .env (
  echo GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 > .env
  echo .env 파일을 생성했습니다.
)

if not exist sheets (
  mkdir sheets
  echo # Initialize sheets package > sheets\__init__.py
  echo sheets 디렉토리를 생성했습니다.
)

if not exist credentials.json (
  echo 경고: credentials.json 파일이 없습니다!
  echo 앱이 제대로 작동하지 않을 수 있습니다.
  echo 계속 진행하시겠습니까? (Y/N)
  set /p continue_choice=선택: 
  if /i NOT "%continue_choice%"=="Y" goto menu
)

echo.
echo 앱을 실행합니다...
echo.

REM 앱 실행
streamlit run app.py

echo.
echo 앱이 종료되었습니다.
pause
goto menu

REM 종료
:end
echo.
echo 프로그램을 종료합니다.
echo. 