@echo off
echo 학원 자동 첨삭 시스템을 시작합니다...
echo.

rem Python 설치 여부 확인
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python이 설치되어 있지 않습니다.
    echo Python을 설치한 후 다시 시도해주세요.
    echo https://www.python.org/downloads/
    pause
    exit /b
)

rem 가상환경 우회하여 직접 실행
python -E no_dependency_app.py

pause 