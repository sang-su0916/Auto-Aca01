@echo off
chcp 65001
title 학원 자동 첨삭 시스템

echo ==================================
echo     학원 자동 첨삭 시스템 실행
echo ==================================
echo.

REM Python 설치 확인
where python >nul 2>nul
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=python
    goto :continue
)

where py >nul 2>nul
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=py
    goto :continue
)

echo Python이 설치되어 있지 않습니다.
echo Python을 설치해주세요: https://www.python.org/downloads/
echo 설치 시 "Add Python to PATH" 옵션을 체크해주세요.
pause
exit /b 1

:continue
echo Python이 확인되었습니다.

REM 필요한 패키지 설치
echo 필요한 패키지를 설치하고 있습니다...
%PYTHON_CMD% -m pip install streamlit pandas --quiet

REM 앱 파일 실행
echo 앱을 시작합니다...
%PYTHON_CMD% -m streamlit run 학원앱.py

pause 