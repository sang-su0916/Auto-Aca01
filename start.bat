@echo off
echo ===================================
echo    학원 자동 첨삭 시스템 시작    
echo ===================================
echo.

py no_dependency_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 오류가 발생했습니다. 다른 방법을 시도합니다...
    echo.
    py -E no_dependency_app.py
)

pause 