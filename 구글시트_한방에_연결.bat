@echo off
chcp 65001 > nul
title 구글 시트 한방에 연결

echo ================================================
echo          구글 시트 한방에 연결 도구
echo ================================================
echo.
echo 구글 시트 ID: 1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0
echo.

:menu
echo 작업을 선택하세요:
echo.
echo [1] 모두 자동으로 설정하기 (권장)
echo [2] 필수 패키지만 설치하기
echo [3] 서비스 계정 이메일 확인하기
echo [4] 앱 실행하기
echo [0] 종료
echo.
set /p choice=선택 (0-4): 

if "%choice%"=="1" goto all_in_one
if "%choice%"=="2" goto install_packages
if "%choice%"=="3" goto check_email
if "%choice%"=="4" goto run_app
if "%choice%"=="0" goto end

echo 잘못된 선택입니다. 다시 시도하세요.
goto menu

:all_in_one
echo.
echo === 전체 설정을 시작합니다 ===
echo.

echo 1단계: .env 파일 생성
echo GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 > .env
echo - .env 파일 생성 완료

echo 2단계: sheets 디렉토리 생성
if not exist sheets mkdir sheets
echo # Initialize sheets package > sheets\__init__.py
echo - sheets 디렉토리 생성 완료

echo 3단계: 필요한 패키지 설치
pip install python-dotenv google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas streamlit
echo - 패키지 설치 완료

echo 4단계: credentials.json 확인
if exist credentials.json (
  echo - credentials.json 파일 확인 완료
  
  echo 5단계: 서비스 계정 이메일 확인
  echo import json > temp_email.py
  echo with open('credentials.json', 'r') as f: >> temp_email.py
  echo     data = json.load(f) >> temp_email.py
  echo     if 'client_email' in data: >> temp_email.py
  echo         print("\n서비스 계정 이메일:", data['client_email']) >> temp_email.py
  echo         print("\n이 이메일을 구글 시트 편집자로 추가하세요.") >> temp_email.py
  echo     else: >> temp_email.py
  echo         print("\n오류: credentials.json에 client_email이 없습니다.") >> temp_email.py
  
  python temp_email.py
  del temp_email.py
  
  echo.
  echo ================================================
  echo 위 이메일을 구글 시트에 '편집자'로 추가하세요:
  echo 1. 구글 시트 접속: https://docs.google.com/spreadsheets/d/1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0
  echo 2. '공유' 버튼 클릭
  echo 3. 위 이메일 주소 입력
  echo 4. '편집자' 권한 선택
  echo 5. '완료' 클릭
  echo ================================================
  echo.
  
) else (
  echo - credentials.json 파일이 없습니다!
  echo   Google Cloud Console에서 서비스 계정 키(JSON)를 다운로드하여 프로젝트 루트에 저장하세요.
)

echo 모든 설정이 완료되었습니다.
echo 계속해서 앱을 실행하시겠습니까? (Y/N)
set /p run_app_choice=선택: 
if /i "%run_app_choice%"=="Y" goto run_app_now

echo.
echo 메인 메뉴로 돌아갑니다.
pause
goto menu

:install_packages
echo.
echo 필요한 패키지를 설치합니다...
pip install python-dotenv google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas streamlit
echo.
echo 패키지 설치가 완료되었습니다.
echo.
pause
goto menu

:check_email
echo.
echo 서비스 계정 이메일을 확인합니다...
echo.

if exist credentials.json (
  echo import json > temp_email.py
  echo with open('credentials.json', 'r') as f: >> temp_email.py
  echo     data = json.load(f) >> temp_email.py
  echo     if 'client_email' in data: >> temp_email.py
  echo         print("서비스 계정 이메일:", data['client_email']) >> temp_email.py
  echo         print("\n이 이메일을 구글 시트 편집자로 추가하세요.") >> temp_email.py
  echo         print("구글 시트 URL: https://docs.google.com/spreadsheets/d/1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0") >> temp_email.py
  echo     else: >> temp_email.py
  echo         print("오류: credentials.json에 client_email이 없습니다.") >> temp_email.py
  
  python temp_email.py
  del temp_email.py
) else (
  echo 오류: credentials.json 파일이 없습니다!
  echo Google Cloud Console에서 서비스 계정 키를 다운로드하여 저장하세요.
)

echo.
pause
goto menu

:run_app
echo.
echo Streamlit 앱을 실행합니다...
echo.

REM .env 파일이 있는지 확인하고 없으면 생성
if not exist .env (
  echo GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 > .env
)

REM sheets 디렉토리가 있는지 확인하고 없으면 생성
if not exist sheets (
  mkdir sheets
  echo # Initialize sheets package > sheets\__init__.py
)

streamlit run app.py

echo.
echo 앱 실행이 종료되었습니다.
pause
goto menu

:run_app_now
echo.
echo Streamlit 앱을 실행합니다...
echo.
streamlit run app.py
echo.
echo 앱 실행이 종료되었습니다.
pause
goto menu

:end
echo.
echo 프로그램을 종료합니다.
echo. 