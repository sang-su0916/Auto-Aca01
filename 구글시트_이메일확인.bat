@echo off
chcp 65001 > nul
title 구글 시트 서비스계정 이메일 확인

echo ================================================
echo       구글 시트 서비스계정 이메일 확인
echo ================================================
echo.

REM credentials.json 파일 확인
if not exist credentials.json (
  echo 오류: credentials.json 파일이 없습니다!
  echo Google Cloud Console에서 서비스 계정 키를 다운로드하여 저장하세요.
  echo.
  echo 계속하려면 아무 키나 누르세요...
  pause > nul
  exit /b 1
)

REM 파이썬 스크립트 생성
echo import json > temp_email.py
echo with open('credentials.json', 'r') as f: >> temp_email.py
echo     data = json.load(f) >> temp_email.py
echo     if 'client_email' in data: >> temp_email.py
echo         print("서비스 계정 이메일:", data['client_email']) >> temp_email.py
echo         print("\n이 이메일을 구글 시트 편집자로 추가하세요.") >> temp_email.py
echo         print("구글 시트 URL: https://docs.google.com/spreadsheets/d/1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0") >> temp_email.py
echo     else: >> temp_email.py
echo         print("오류: credentials.json에 client_email이 없습니다.") >> temp_email.py

REM 스크립트 실행
python temp_email.py

REM 임시 파일 삭제
del temp_email.py

echo.
echo ================================================
echo 위 이메일을 구글 시트에 '편집자'로 추가하세요:
echo 1. 구글 시트에서 '공유' 버튼 클릭
echo 2. 위 이메일 주소 입력
echo 3. '편집자' 권한 선택
echo 4. '완료' 클릭
echo ================================================
echo.
echo 계속하려면 아무 키나 누르세요...
pause > nul 