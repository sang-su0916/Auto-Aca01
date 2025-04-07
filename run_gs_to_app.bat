@echo off
echo 구글 시트에서 앱으로 데이터 가져오기를 시작합니다...
echo.

REM 가상환경 활성화
echo 가상환경을 활성화합니다...
call .\sheets_venv\Scripts\activate.bat

REM 스크립트 실행
echo.
echo 구글 시트 데이터를 앱으로 가져오는 중...
python gs_to_app.py

echo.
echo 완료되었습니다. 아무 키나 눌러 종료하세요...
pause 