@echo off
chcp 65001 > nul
title 구글 시트 설정

echo ================================================
echo         구글 시트 연동 설정 도우미
echo ================================================
echo.
echo 구글 시트 ID: 1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0
echo.

:menu
echo 작업을 선택하세요:
echo.
echo [1] 구글 시트 연결 확인
echo [2] 구글 시트 초기화 (.env 파일 업데이트 + 시트 헤더 설정)
echo [3] 앱 실행하기
echo [0] 종료
echo.
set /p choice=선택 (0-3): 

if "%choice%"=="1" goto check_connection
if "%choice%"=="2" goto initialize_sheet
if "%choice%"=="3" goto run_app
if "%choice%"=="0" goto end

echo 잘못된 선택입니다. 다시 시도하세요.
goto menu

:check_connection
echo.
echo 구글 시트 연결을 확인합니다...
echo.
echo 필요한 모듈 설치 중...
pip install python-dotenv pandas google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client streamlit
echo.
python check_sheets_connection.py
echo.
pause
goto menu

:initialize_sheet
echo.
echo 구글 시트를 초기화합니다...
echo.
echo 필요한 모듈 설치 중...
pip install python-dotenv pandas google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client streamlit
echo.
python update_sheets_id.py
echo.
python init_sheets.py
echo.
pause
goto menu

:run_app
echo.
echo 앱을 실행합니다...
echo.
streamlit run app.py
echo.
pause
goto menu

:end
echo.
echo 프로그램을 종료합니다.
echo. 