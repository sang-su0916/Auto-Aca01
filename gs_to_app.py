#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
구글 시트 문제 데이터를 가져와 앱에 바로 저장하는 통합 스크립트
"""

import os
import json
import shutil
import sys
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 구글 시트 설정
CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0')

# 앱 데이터 파일 경로
APP_DATA_DIR = "data"
PROBLEMS_FILE = os.path.join(APP_DATA_DIR, "problems.json")
TEMP_JSON_FILE = "temp_problems.json"  # 임시 JSON 파일
BACKUP_DIR = os.path.join(APP_DATA_DIR, "backups")

def ensure_dirs_exist():
    """필요한 디렉토리가 존재하는지 확인하고, 없으면 생성"""
    if not os.path.exists(APP_DATA_DIR):
        os.makedirs(APP_DATA_DIR)
        print(f"'{APP_DATA_DIR}' 디렉토리를 생성했습니다.")
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"'{BACKUP_DIR}' 디렉토리를 생성했습니다.")

def backup_existing_file():
    """기존 파일 백업"""
    if os.path.exists(PROBLEMS_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"problems_{timestamp}.json"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        shutil.copy2(PROBLEMS_FILE, backup_path)
        print(f"기존 파일을 '{backup_path}'로 백업했습니다.")
        return True
    return False

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
        print("Google Sheets API 서비스가 성공적으로 초기화되었습니다.")
        return service
    except Exception as e:
        print(f"Google Sheets API 초기화 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def fetch_problems_from_sheet(service, sheet_name='problems'):
    """문제 데이터 가져오기"""
    try:
        # 데이터 가져오기
        range_name = f'{sheet_name}!A:N'  # A부터 N열까지 모든 데이터
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("스프레드시트에 데이터가 없습니다.")
            return []
        
        # 헤더 가져오기
        headers = values[0]
        
        # 데이터 가져오기 (헤더 제외)
        data = values[1:]
        
        # 문제 리스트 생성
        problems = []
        for row in data:
            # 누락된 필드 채우기
            while len(row) < len(headers):
                row.append('')
            
            # 문제 딕셔너리 생성
            problem = {}
            for i, header in enumerate(headers):
                problem[header] = row[i]
            
            problems.append(problem)
        
        print(f"Google Sheets에서 {len(problems)}개의 문제를 가져왔습니다.")
        return problems
    except HttpError as error:
        print(f"Google Sheets API 오류: {error}")
        return []
    except Exception as e:
        print(f"문제 데이터 가져오기 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def save_to_app(data):
    """데이터를 앱에 저장"""
    try:
        with open(PROBLEMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"데이터를 앱의 '{PROBLEMS_FILE}' 파일에 성공적으로 저장했습니다.")
        return True
    except Exception as e:
        print(f"앱에 데이터 저장 중 오류 발생: {str(e)}")
        return False

def main():
    print("구글 시트 문제 데이터를 앱에 업로드하는 통합 스크립트를 시작합니다...")
    
    # 명령줄 인수 처리
    if len(sys.argv) > 1:
        sheet_name = sys.argv[1]
    else:
        sheet_name = 'problems'  # 기본 시트 이름
    
    # 필요한 디렉토리 확인 및 생성
    ensure_dirs_exist()
    
    # 기존 파일 백업
    backup_existing_file()
    
    # 서비스 생성
    service = create_sheets_service()
    if not service:
        print("구글 시트 API 서비스 초기화에 실패했습니다.")
        return
    
    # 스프레드시트 정보 확인
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        print(f"스프레드시트 이름: {spreadsheet['properties']['title']}")
        
        # 시트 목록 가져오기
        sheets = spreadsheet.get('sheets', [])
        sheet_titles = [sheet['properties']['title'] for sheet in sheets]
        
        # 지정된 시트가 없는 경우 첫 번째 시트 사용
        if sheet_name not in sheet_titles:
            print(f"시트 '{sheet_name}'을(를) 찾을 수 없습니다. 대신 첫 번째 시트를 사용합니다.")
            sheet_name = sheet_titles[0]
            
        print(f"\n'{sheet_name}' 시트에서 데이터를 가져오는 중...")
        problems = fetch_problems_from_sheet(service, sheet_name)
        
        if problems:
            # 앱에 데이터 저장
            if save_to_app(problems):
                print(f"\n변환 및 업로드 완료! 앱이 이제 새 문제 데이터를 사용할 수 있습니다.")
                print(f"총 {len(problems)}개의 문제가 업로드되었습니다.")
            else:
                print("\n앱에 데이터 저장 중 오류가 발생했습니다.")
        else:
            print("\n가져올 데이터가 없습니다.")
    
    except HttpError as error:
        print(f"Google Sheets API 오류: {error}")
    except Exception as e:
        print(f"처리 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 