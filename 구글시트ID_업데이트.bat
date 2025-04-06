@echo off
chcp 65001 > nul
title 구글 시트 ID 업데이트

echo ================================================
echo      구글 시트 ID 업데이트
echo ================================================
echo.
echo 구글 시트 ID: 1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0
echo.

REM 간단한 Python 스크립트 실행
python update_sheets_id.py

echo.
echo 설정이 완료되었습니다.
echo 계속하려면 아무 키나 누르세요...
pause > nul 