#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
구글 시트 연결 확인 스크립트
"""

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 구글 시트 ID
SPREADSHEET_ID = "1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def check_connection():
    """구글 시트 연결 테스트"""
    print(f"구글 시트 ID: {SPREADSHEET_ID}")
    
    # 인증 정보 파일 확인
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"오류: {CREDENTIALS_FILE} 파일을 찾을 수 없습니다.")
        return False
    
    try:
        # 인증 정보 생성
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        
        # 서비스 계정 이메일 출력
        print(f"서비스 계정 이메일: {credentials.service_account_email}")
        print("* 위 이메일에 구글 시트 편집 권한을 부여해야 합니다.")
        
        # 서비스 객체 생성
        service = build('sheets', 'v4', credentials=credentials)
        
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
        
        # 시트 데이터 확인
        sheet_name = sheets[0]['properties']['title']
        print(f"\n시트 '{sheet_name}'의 데이터 확인 중...")
        
        # A1:N10 범위의 데이터 가져오기
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A1:N10"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("시트에 데이터가 없습니다.")
        else:
            print(f"시트에 데이터가 있습니다. 첫 행: {values[0]}")
            print(f"총 {len(values)} 행의 데이터가 있습니다.")
        
        print("\n✅ 구글 시트 연결이 정상적으로 작동합니다!")
        return True
    
    except HttpError as error:
        if error.resp.status == 404:
            print(f"❌ 오류: 스프레드시트를 찾을 수 없습니다. ID: {SPREADSHEET_ID}")
            print("스프레드시트 ID가 올바른지 확인하세요.")
        elif error.resp.status == 403:
            print(f"❌ 오류: 스프레드시트 접근 권한이 없습니다. ID: {SPREADSHEET_ID}")
            print("서비스 계정 이메일에 스프레드시트 편집 권한을 부여했는지 확인하세요.")
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
    check_connection()
    print("\n테스트가 완료되었습니다.") 