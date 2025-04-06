#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
구글 시트 연결 문제 해결 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

# 현재 경로 출력
print(f"현재 작업 디렉토리: {os.getcwd()}")

# 환경 변수 파일 확인
env_file = Path('.env')
if env_file.exists():
    print("\n.env 파일이 존재합니다.")
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"내용: {content}")
else:
    print("\n.env 파일이 존재하지 않습니다. 새로 생성합니다.")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write("GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0\n")
    print(".env 파일이 생성되었습니다.")

# credentials.json 파일 확인
creds_file = Path('credentials.json')
if creds_file.exists():
    print("\ncredentials.json 파일이 존재합니다.")
else:
    print("\ncredentials.json 파일이 존재하지 않습니다.")
    print("Google Cloud Console에서 서비스 계정 키(JSON)를 다운로드하여 프로젝트 루트에 저장하세요.")

# 필수 모듈 설치
print("\n필요한 Python 모듈을 설치합니다...")
packages = [
    "python-dotenv",
    "google-auth",
    "google-auth-oauthlib",
    "google-auth-httplib2", 
    "google-api-python-client",
    "pandas"
]

for package in packages:
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package], check=True)
        print(f"{package} 설치 완료")
    except subprocess.CalledProcessError:
        print(f"{package} 설치 중 오류가 발생했습니다.")

# 구글 시트 이메일 권한 확인
print("\n구글 시트 접근 권한 확인:")
print("1. https://docs.google.com/spreadsheets/d/1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0 에 접속")
print("2. '공유' 버튼 클릭")
print("3. credentials.json에 있는 client_email 값을 확인하여 '편집자' 권한으로 추가")

# 시스템 환경 확인
print("\n시스템 환경 확인:")
print(f"Python 버전: {sys.version}")
print(f"운영체제: {sys.platform}")

print("\n문제 해결이 완료되었습니다.")
print("연결 테스트를 위해 다음 명령을 실행하세요:")
print("python check_sheets_connection.py") 