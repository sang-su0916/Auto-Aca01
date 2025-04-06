@echo off
chcp 65001 > nul
title 시스템 명령으로 구글 시트 연동 해결

echo ================================================
echo      시스템 명령으로 구글 시트 연동 해결
echo ================================================
echo.

REM 환경 변수 파일 생성
echo GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 > .env
echo ✓ .env 파일 생성 완료

REM sheets 디렉토리 생성
if not exist sheets mkdir sheets
echo # Initialize sheets package > sheets\__init__.py
echo ✓ sheets 디렉토리 설정 완료

REM 필수 패키지 설치 (글로벌로 설치)
echo.
echo 필수 패키지를 글로벌 모드로 설치합니다...
echo 이 과정은 몇 분 정도 소요될 수 있습니다...
echo.

REM 각 패키지를 개별적으로 설치
call pip install --upgrade --no-warn-script-location python-dotenv
echo ✓ python-dotenv 설치 완료

call pip install --upgrade --no-warn-script-location google-auth
echo ✓ google-auth 설치 완료

call pip install --upgrade --no-warn-script-location google-auth-oauthlib
echo ✓ google-auth-oauthlib 설치 완료

call pip install --upgrade --no-warn-script-location google-auth-httplib2
echo ✓ google-auth-httplib2 설치 완료

call pip install --upgrade --no-warn-script-location google-api-python-client
echo ✓ google-api-python-client 설치 완료

call pip install --upgrade --no-warn-script-location pandas
echo ✓ pandas 설치 완료

call pip install --upgrade --no-warn-script-location streamlit
echo ✓ streamlit 설치 완료

echo.
echo ================================================
echo 설정이 완료되었습니다!
echo.
echo credentials.json 파일이 프로젝트 루트 폴더에 있는지 확인하세요.
echo.
echo 앱을 실행하려면 다음 명령어를 입력하세요:
echo streamlit run app.py
echo ================================================

echo.
echo 계속하려면 아무 키나 누르세요...
pause > nul 