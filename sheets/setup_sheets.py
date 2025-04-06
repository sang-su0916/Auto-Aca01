#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
from pathlib import Path
import traceback

print("\n===== 구글 시트 설정 및 연결 테스트 =====")

# 필요한 모듈 설치 시도
try:
    import pandas as pd
    import google.oauth2.service_account
    import googleapiclient.discovery
    import dotenv
    from dotenv import load_dotenv
    from google.oauth2.service_account import Credentials
    print("필요한 패키지가 모두 설치되어 있습니다.")
except ImportError:
    print("필요한 패키지를 설치합니다...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "google-auth", "google-api-python-client", "python-dotenv"])
    
    # 다시 임포트
    import pandas as pd
    import google.oauth2.service_account
    import googleapiclient.discovery
    from dotenv import load_dotenv
    from google.oauth2.service_account import Credentials
    print("패키지 설치가 완료되었습니다.")

# 환경 변수 로드
load_dotenv()

# 상수 정의
CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0')

print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"설정할 인증 파일 경로: {os.path.abspath(CREDENTIALS_FILE)}")
print(f"스프레드시트 ID: {SPREADSHEET_ID}")

# 환경 변수 파일 생성 (.env)
try:
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(f'GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID}\n')
    print(f"환경 변수 파일 .env가 생성되었습니다.")
except Exception as e:
    print(f"환경 변수 파일 생성 오류: {str(e)}")
    traceback.print_exc()

# 인증 정보 파일 확인
if not os.path.exists(CREDENTIALS_FILE):
    print(f"\n경고: {CREDENTIALS_FILE} 파일이 존재하지 않습니다.")
    print("Google 서비스 계정 자격 증명 파일을 수동으로 다운로드하여 프로젝트 루트에 'credentials.json'으로 저장해주세요.")
    print("자격 증명은 Google Cloud Console에서 생성할 수 있습니다: https://console.cloud.google.com/")
    
    # 샘플 형식 안내
    print("\n인증 정보 파일의 형식은 다음과 같습니다:")
    print('''{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-email%40your-project.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}''')
    sys.exit(1)
else:
    print(f"인증 정보 파일 {CREDENTIALS_FILE}이 존재합니다.")

# 연결 테스트
try:
    print("\n구글 시트 연결을 테스트합니다...")
    
    # 인증 정보 생성
    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES)
    
    # 서비스 객체 생성
    service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
    
    # 연결 테스트
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID).execute()
    
    print(f"연결 성공! 스프레드시트 타이틀: '{spreadsheet['properties']['title']}'")
    print("Google Sheets API 연결 테스트에 성공했습니다!")
    print("\n===== 구글 시트 설정 완료 =====")
    print("앱을 실행할 준비가 되었습니다.")
except Exception as e:
    print(f"구글 시트 연결 테스트 오류: {str(e)}")
    traceback.print_exc()
    print("Google Sheets API 연결 테스트에 실패했습니다.")
    sys.exit(1)