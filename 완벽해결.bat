@echo off
echo ================================================
echo         구글 시트 연동 완벽 해결 도구
echo ================================================
echo.

echo 구글 시트 연동 문제를 완벽하게 해결합니다...
echo.

REM Python 환경 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요.
    pause
    exit /b
)

REM 스크립트 실행
python complete_fix.py

REM 앱 실행 여부 확인
echo.
echo 모든 문제가 해결되었습니다. 앱을 실행할까요? (Y/N)
choice /c YN /n
if %errorlevel% equ 1 (
    echo.
    echo 앱을 실행합니다...
    python app.py
)

echo.
echo 작업이 완료되었습니다.
echo.
pause 