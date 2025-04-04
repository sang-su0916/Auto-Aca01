@echo off
title 학원 자동 첨삭 시스템
color 0A
mode con cols=90 lines=30

echo ================================================================================
echo.
echo                            학원 자동 첨삭 시스템 시작 
echo.
echo ================================================================================
echo.
echo  프로그램을 시작합니다. 잠시만 기다려주세요...
echo.

:: Python 확인
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py auto_start.py
    exit /b
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python auto_start.py
    exit /b
)

:: 둘 다 실패하면 직접 실행 시도
start "" "start.bat"

:: 3초 대기
timeout /t 3 /nobreak >nul

:: 만약 start.bat 실행도 실패하면
echo.
echo Python이 설치되어 있지 않거나 경로가 설정되지 않았습니다.
echo 다음 순서대로 시도해 보세요:
echo.
echo 1. Python 설치 (https://www.python.org/downloads/)
echo 2. 설치 시 "Add Python to PATH" 옵션 선택
echo 3. 컴퓨터 재시작 후 다시 시도
echo.
echo 4. 또는 직접 실행: no_dependency_app.py를 마우스 오른쪽 버튼으로 클릭하고
echo    "Python으로 실행" 선택
echo.

pause 