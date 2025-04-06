@echo off
echo 구글 시트 연동 앱을 실행합니다...

REM 가상환경 활성화
call sheets_venv\Scripts\activate.bat

REM 앱 실행
streamlit run app.py

REM 스크립트 종료 시 가상환경 비활성화
call deactivate
pause 