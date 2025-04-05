@echo off
title 학원 자동 첨삭 시스템
echo.
echo 학원 자동 첨삭 시스템을 시작합니다...
echo.

REM Python 설치 확인
where python >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Python이 설치되어 있습니다.
    set PYTHON_CMD=python
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% == 0 (
        echo Python이 설치되어 있습니다.
        set PYTHON_CMD=py
    ) else (
        echo Python이 설치되어 있지 않습니다. 
        echo Python을 설치한 후 다시 시도해 주세요.
        echo https://www.python.org/downloads/
        pause
        exit /b
    )
)

REM 필요한 패키지 설치
echo 필요한 패키지를 확인합니다...
%PYTHON_CMD% -m pip install -q streamlit pandas

REM 앱 실행
echo 학원 자동 첨삭 시스템을 시작합니다...
start "" http://localhost:8501
%PYTHON_CMD% -m streamlit run app_without_sheets.py

pause 