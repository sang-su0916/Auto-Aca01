#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
구글 시트 연동 Streamlit 앱 실행 스크립트
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# 환경 변수 로드
load_dotenv()

# 구글 시트 ID 확인
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
if not SPREADSHEET_ID:
    print("경고: .env 파일에 GOOGLE_SHEETS_SPREADSHEET_ID가 설정되지 않았습니다.")
    print("기본값으로 설정합니다.")
    SPREADSHEET_ID = "1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0"
    
    # .env 파일에 ID 추가
    with open('.env', 'a', encoding='utf-8') as f:
        f.write(f"GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID}\n")
    
    print(f"GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID} 환경 변수가 설정되었습니다.")
    # 환경 변수 다시 로드
    load_dotenv(override=True)

# 필요한 디렉토리 확인 및 생성
sheets_dir = Path('sheets')
if not sheets_dir.exists():
    print("sheets 디렉터리가 없습니다. 생성합니다.")
    sheets_dir.mkdir()
    
    # __init__.py 파일 생성
    init_file = sheets_dir / "__init__.py"
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write("# Initialize the sheets package\n")

# 인증 파일 확인
credentials_file = Path('credentials.json')
if not credentials_file.exists():
    print("경고: credentials.json 파일이 없습니다!")
    print("Google Cloud Console에서 서비스 계정 키(JSON)를 다운로드하여 프로젝트 루트에 저장하세요.")
    sys.exit(1)

# 구글 시트 연결 테스트
print("구글 시트 연결을 테스트합니다...")
try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    
    credentials = Credentials.from_service_account_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    
    # 스프레드시트 정보 가져오기
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID).execute()
    
    print(f"✅ 구글 시트 연결 성공! 스프레드시트 이름: '{spreadsheet['properties']['title']}'")
    print(f"스프레드시트 URL: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
    
    # 서비스 계정 이메일 출력
    print(f"서비스 계정 이메일: {credentials.service_account_email}")
    print("이 이메일에 구글 시트 편집 권한이 부여되어 있는지 확인하세요.")
    
except Exception as e:
    print(f"❌ 구글 시트 연결 오류: {str(e)}")
    print("\n권한 문제가 있는 경우:")
    print("1. 구글 스프레드시트에서 '공유' 버튼 클릭")
    print("2. 서비스 계정 이메일(위에 표시된) 입력")
    print("3. '편집자' 권한 선택 후 '완료' 클릭")
    print("\n계속 진행하시겠습니까? (y/n): ", end="")
    choice = input().lower()
    if choice != 'y':
        sys.exit(1)

# Streamlit 앱 실행
print("\nStreamlit 앱을 실행합니다...")
time.sleep(1)

# Streamlit 실행 명령어
streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
try:
    subprocess.run(streamlit_cmd)
except KeyboardInterrupt:
    print("\n앱 실행이 중단되었습니다.")
except Exception as e:
    print(f"\n앱 실행 중 오류 발생: {str(e)}")
    
    # 대체 실행 방법 시도
    print("\n대체 방법으로 앱 실행을 시도합니다...")
    try:
        os.system("streamlit run app.py")
    except Exception as e2:
        print(f"앱 실행 실패: {str(e2)}")
        print("\n문제 해결 방법:")
        print("1. pip install streamlit 명령으로 Streamlit을 설치하세요.")
        print("2. 설치 후 'streamlit run app.py' 명령을 직접 실행하세요.") 