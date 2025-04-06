#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
구글 시트 연결 유틸리티 스크립트
"""

import os
import sys
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# .env 파일 로드
load_dotenv()

# 구글 시트 ID - 환경 변수에서 가져오기
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0')
CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def create_sheets_service():
    """Google Sheets API 서비스 객체 생성"""
    try:
        # 인증 정보 파일 확인
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"오류: {CREDENTIALS_FILE} 파일을 찾을 수 없습니다.")
            return None

        # 인증 정보 생성
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        
        # 서비스 객체 생성
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"Google Sheets API 초기화 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_sheets_connection():
    """구글 시트 연결 테스트"""
    print(f"구글 시트 ID: {SPREADSHEET_ID}")
    
    # 서비스 객체 생성
    service = create_sheets_service()
    if not service:
        print("Google Sheets API 서비스를 초기화할 수 없습니다.")
        return False
    
    try:
        # 스프레드시트 정보 가져오기
        print("\n구글 시트 정보 조회 중...")
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID).execute()
        
        print(f"✅ 연결 성공! 스프레드시트 타이틀: '{spreadsheet['properties']['title']}'")
        
        # 시트 목록 확인
        sheets = spreadsheet.get('sheets', [])
        print("\n시트 목록:")
        for sheet in sheets:
            print(f"  - {sheet['properties']['title']}")
        
        print("\n✅ 구글 시트 연결이 정상적으로 작동합니다!")
        return True
    
    except HttpError as error:
        if error.resp.status == 404:
            print(f"❌ 오류: 스프레드시트를 찾을 수 없습니다. ID: {SPREADSHEET_ID}")
        elif error.resp.status == 403:
            print(f"❌ 오류: 스프레드시트 접근 권한이 없습니다. ID: {SPREADSHEET_ID}")
            print("\n권한 부여 방법:")
            print("1. 구글 스프레드시트에서 '공유' 버튼 클릭")
            print("2. 서비스 계정 이메일 입력")
            print("3. '편집자' 권한 선택 후 '완료' 클릭")
        else:
            print(f"❌ 구글 시트 API 오류: {error}")
        return False
    
    except Exception as e:
        print(f"❌ 연결 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("===== 구글 시트 연결 테스트 =====\n")
    test_sheets_connection()
    print("\n테스트가 완료되었습니다.") 