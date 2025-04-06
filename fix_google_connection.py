#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import traceback
from dotenv import load_dotenv

def fix_google_sheets_connection():
    """
    구글 시트 연동 문제 해결 스크립트
    """
    print("=" * 60)
    print("    구글 시트 연동 문제 해결 도구")
    print("=" * 60)
    print()

    # 환경 변수 로드
    load_dotenv()
    
    # 1. logic 디렉토리 확인 및 생성
    if not os.path.exists('logic'):
        print("logic 디렉토리가 없습니다. 생성합니다...")
        os.makedirs('logic', exist_ok=True)
        print("✓ logic 디렉토리 생성 완료")
    else:
        print("✓ logic 디렉토리 확인 완료")
    
    # 2. logic/__init__.py 확인
    if not os.path.exists('logic/__init__.py'):
        print("logic/__init__.py 파일이 없습니다. 생성합니다...")
        with open('logic/__init__.py', 'w', encoding='utf-8') as f:
            f.write("""# Logic package initialization
from logic.grader import Grader
from logic.autograder import AutoGrader

__all__ = ['Grader', 'AutoGrader']
""")
        print("✓ logic/__init__.py 파일 생성 완료")
    else:
        print("✓ logic/__init__.py 파일 확인 완료")
    
    # 3. 필요한 패키지 설치 확인
    try:
        import pandas
        import google.oauth2
        import googleapiclient
        print("✓ 필요한 패키지 설치 확인 완료")
    except ImportError as e:
        print(f"패키지가 설치되어 있지 않습니다: {str(e)}")
        print("필요한 패키지를 설치합니다...")
        os.system("pip install -r requirements.txt")
        print("패키지 설치 완료")
    
    # 4. credentials.json 파일 확인
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json 파일이 없습니다.")
        print("Google Cloud Console에서 서비스 계정 키를 다운로드하여 credentials.json으로 저장해주세요.")
        print("https://console.cloud.google.com/apis/credentials")
    else:
        print("✓ credentials.json 파일 확인 완료")
    
    # 5. .env 파일 업데이트
    spreadsheet_id = os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID', '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0')
    
    try:
        with open(".env", "w") as f:
            f.write("# Google Sheets API Configuration\n")
            f.write(f"GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}")
        print(f"✓ .env 파일 업데이트 완료 (Spreadsheet ID: {spreadsheet_id})")
    except Exception as e:
        print(f"❌ .env 파일 업데이트 실패: {str(e)}")
    
    # 6. Google Sheets 연결 테스트
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        # 서비스 계정 인증 정보 로드
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        
        # 스프레드시트 정보 가져오기
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        print(f"✓ 구글 스프레드시트 연결 성공! 시트 이름: {spreadsheet.get('properties', {}).get('title', '제목 없음')}")
        sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
        print(f"  시트 목록: {', '.join(sheets)}")
        
        # 필요한 시트 생성 여부 확인
        required_sheets = ['problems', 'student_answers']
        missing_sheets = [sheet for sheet in required_sheets if sheet not in sheets]
        
        if missing_sheets:
            print(f"  필요한 시트가 없습니다: {', '.join(missing_sheets)}")
            print("  setup_and_connect.py 스크립트를 실행하여 필요한 시트를 생성하세요.")
        else:
            print("  필요한 모든 시트가 존재합니다.")
        
    except Exception as e:
        print(f"❌ 구글 스프레드시트 연결 테스트 실패: {str(e)}")
        print("다음 사항을 확인해주세요:")
        print("1. credentials.json 파일이 유효한지 확인")
        print("2. 스프레드시트 ID가 올바른지 확인")
        print("3. 서비스 계정에 스프레드시트 접근 권한이 있는지 확인")
    
    print("\n모든 검사를 완료했습니다.")
    print("앱을 재시작하여 구글 시트 연동이 정상 작동하는지 확인해주세요.")
    return True

if __name__ == "__main__":
    try:
        fix_google_sheets_connection()
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        traceback.print_exc()
    
    input("\n아무 키나 눌러 종료하세요...") 