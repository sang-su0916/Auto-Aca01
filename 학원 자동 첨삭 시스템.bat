@echo off
echo 학원 자동 첨삭 시스템을 실행합니다...

:: Python 설치 확인
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Python이 설치되어 있습니다.
    goto :python_found
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    echo Python이 설치되어 있습니다.
    goto :python_found
)

echo Python이 설치되어 있지 않습니다.
echo https://www.python.org/downloads/ 에서 Python을 설치한 후 다시 실행해주세요.
pause
exit /b 1

:python_found
:: 필요한 패키지 설치
echo 필요한 패키지를 설치합니다...
python -m pip install streamlit pandas -q

:: 앱 실행
echo 학원 자동 첨삭 시스템 시작 중...

:: 파일 존재 확인
if exist "app_without_google.py" (
    :: 브라우저 열기
    start http://localhost:8501
    :: 애플리케이션 실행
    python -m streamlit run app_without_google.py
) else (
    echo app_without_google.py 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

pause 