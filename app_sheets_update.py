#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
구글 시트 연동 업데이트 스크립트
지정된 구글 시트 ID로 환경 변수를 업데이트합니다.
"""

import os
import sys
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 구글 시트 ID
SPREADSHEET_ID = "1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0"

# 상수 정의
CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def update_env_file():
    """환경 변수 파일 업데이트"""
    # .env 파일이 존재하는지 확인
    if not os.path.exists('.env'):
        print("경고: .env 파일이 존재하지 않습니다. 새로 생성합니다.")
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID}\n")
        print(".env 파일이 생성되었습니다.")
        return True

    # 기존 .env 파일 읽기
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()

    # GOOGLE_SHEETS_SPREADSHEET_ID 환경 변수가 있는지 확인
    if 'GOOGLE_SHEETS_SPREADSHEET_ID=' in content:
        # 기존 ID 업데이트
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('GOOGLE_SHEETS_SPREADSHEET_ID='):
                lines[i] = f'GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID}'
                break
        
        new_content = '\n'.join(lines)
    else:
        # 새 ID 추가
        if not content.endswith('\n'):
            content += '\n'
        new_content = content + f'GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID}\n'

    # 환경 변수 파일 업데이트
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f".env 파일이 업데이트되었습니다. 스프레드시트 ID: {SPREADSHEET_ID}")
    return True

def create_service():
    """Google Sheets API 서비스 객체 생성"""
    try:
        # 인증 정보 파일 확인
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"오류: {CREDENTIALS_FILE} 파일을 찾을 수 없습니다.")
            print("Google Cloud Console에서 서비스 계정 키(JSON)를 다운로드하여 프로젝트 루트에 저장하세요.")
            return None

        # 인증 정보 생성
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        
        # 서비스 객체 생성
        service = build('sheets', 'v4', credentials=credentials)
        print("Google Sheets API 서비스가 성공적으로 초기화되었습니다.")
        return service
    except Exception as e:
        print(f"Google Sheets API 초기화 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_connection(service, spreadsheet_id):
    """구글 시트 연결 테스트"""
    try:
        # 스프레드시트 정보 가져오기
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id).execute()
        
        print(f"✅ 구글 시트 연결 테스트 성공! 타이틀: '{spreadsheet['properties']['title']}'")
        
        # 시트 목록 확인
        sheets = spreadsheet.get('sheets', [])
        print("시트 목록:")
        for sheet in sheets:
            print(f"  - {sheet['properties']['title']}")
        
        return True
    except HttpError as error:
        if error.resp.status == 404:
            print(f"❌ 오류: 스프레드시트를 찾을 수 없습니다. ID: {spreadsheet_id}")
            print("스프레드시트 ID가 올바른지 확인하세요.")
        elif error.resp.status == 403:
            print(f"❌ 오류: 스프레드시트 접근 권한이 없습니다. ID: {spreadsheet_id}")
            print("서비스 계정 이메일에 스프레드시트 편집 권한을 부여했는지 확인하세요.")
            credentials = Credentials.from_service_account_file(CREDENTIALS_FILE)
            print(f"서비스 계정 이메일: {credentials.service_account_email}")
        else:
            print(f"❌ 구글 시트 API 오류: {error}")
        return False
    except Exception as e:
        print(f"❌ 연결 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def share_spreadsheet(service, spreadsheet_id):
    """스프레드시트 공유 설정"""
    try:
        # Drive API 서비스 생성
        drive_service = build('drive', 'v3', credentials=service._credentials)
        
        # 서비스 계정 이메일 가져오기
        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE)
        service_account_email = credentials.service_account_email
        
        # 공유 설정
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body={
                'type': 'user',
                'role': 'writer',
                'emailAddress': service_account_email
            }
        ).execute()
        
        print(f"스프레드시트가 서비스 계정({service_account_email})과 공유되었습니다.")
        print("이제 앱에서 스프레드시트에 접근할 수 있습니다.")
        
        return True
    except Exception as e:
        print(f"스프레드시트 공유 설정 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def update_sheets_init():
    """sheets/__init__.py 업데이트"""
    # sheets 디렉토리 확인
    if not os.path.exists('sheets'):
        print("sheets 디렉토리가 없습니다. 생성합니다.")
        os.makedirs('sheets', exist_ok=True)
    
    # __init__.py 파일 생성 또는 업데이트
    with open('sheets/__init__.py', 'w', encoding='utf-8') as f:
        f.write("# Initialize the sheets package\n")
    
    print("sheets/__init__.py 파일이 업데이트되었습니다.")
    return True

def main():
    """메인 실행 함수"""
    print("===== 구글 시트 연동 업데이트 =====")
    print(f"사용할 스프레드시트 ID: {SPREADSHEET_ID}")
    
    # .env 파일 업데이트
    if not update_env_file():
        print("환경 변수 업데이트에 실패했습니다.")
        return False
    
    # 환경 변수 다시 로드
    load_dotenv(override=True)
    
    # sheets/__init__.py 업데이트
    if not update_sheets_init():
        print("sheets/__init__.py 업데이트에 실패했습니다.")
    
    # 서비스 객체 생성
    service = create_service()
    if not service:
        print("Google Sheets API 서비스를 초기화할 수 없습니다.")
        return False
    
    # 연결 테스트
    if not test_connection(service, SPREADSHEET_ID):
        print("구글 시트 연결 테스트에 실패했습니다.")
        return False
    
    # 스프레드시트 공유 설정
    if not share_spreadsheet(service, SPREADSHEET_ID):
        print("스프레드시트 공유 설정에 실패했습니다.")
    
    print("\n===== 구글 시트 연동 완료 =====")
    print(f"스프레드시트 ID: {SPREADSHEET_ID}")
    print("연동이 완료되었습니다. 이제 앱에서 구글 시트 데이터를 사용할 수 있습니다.")
    print("\n다음 명령으로 연동 테스트를 실행할 수 있습니다:")
    print("python test_google_sheets.py")
    return True

if __name__ == "__main__":
    main() 