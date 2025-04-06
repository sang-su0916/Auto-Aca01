@echo off
chcp 65001 > nul
title 구글 시트 연동 문제 해결

echo ================================================
echo         구글 시트 연동 문제 해결 도구
echo ================================================
echo.
echo 구글 시트 ID: 1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0
echo.

:menu
echo 작업을 선택하세요:
echo.
echo [1] 필수 모듈 설치하기
echo [2] 환경 설정 확인 및 고치기
echo [3] 구글 시트 연결 테스트
echo [4] 앱 실행하기
echo [0] 종료
echo.
set /p choice=선택 (0-4): 

if "%choice%"=="1" goto install_modules
if "%choice%"=="2" goto fix_environment
if "%choice%"=="3" goto test_connection
if "%choice%"=="4" goto run_app
if "%choice%"=="0" goto end

echo 잘못된 선택입니다. 다시 시도하세요.
goto menu

:install_modules
echo.
echo 필요한 모듈을 설치합니다...
pip install python-dotenv pandas google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client streamlit
echo.
pause
goto menu

:fix_environment
echo.
echo 환경 설정을 확인하고 고칩니다...
python fix_sheets_connection.py
echo.
pause
goto menu

:test_connection
echo.
echo 구글 시트 연결을 테스트합니다...
python check_sheets_connection.py
echo.
pause
goto menu

:run_app
echo.
echo 앱을 실행합니다...
python run_with_sheets.py
echo.
pause
goto menu

:end
echo.
echo 종료합니다.
echo.
exit 