#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
구글 시트 문제 데이터를 JSON으로 변환하는 스크립트
"""

import os
import json
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 구글 시트 설정
CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0')

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

def save_to_json(problems, filename='problems.json'):
    """문제 데이터를 JSON 파일로 저장"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(problems, f, ensure_ascii=False, indent=4)
        print(f"{len(problems)}개의 문제가 {filename} 파일에 저장되었습니다.")
        return True
    except Exception as e:
        print(f"JSON 파일 저장 오류: {str(e)}")
        return False

def main():
    print("구글 시트 문제 데이터를 JSON으로 변환하는 스크립트를 시작합니다...")
    
    # 서비스 생성
    service = create_sheets_service()
    if not service:
        print("구글 시트 API 서비스 초기화에 실패했습니다.")
        return
    
    # 스프레드시트 정보 확인
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        print(f"스프레드시트 이름: {spreadsheet['properties']['title']}")
        
        # 시트 목록 표시
        sheets = spreadsheet.get('sheets', [])
        print("\n사용 가능한 시트 목록:")
        for i, sheet in enumerate(sheets):
            sheet_title = sheet['properties']['title']
            print(f"{i+1}. {sheet_title}")
        
        # 사용자에게 어떤 시트를 사용할지 물어보기
        sheet_idx = input("\n몇 번 시트의 데이터를 JSON으로 변환하시겠습니까? (번호 입력): ")
        try:
            sheet_idx = int(sheet_idx) - 1
            if 0 <= sheet_idx < len(sheets):
                sheet_name = sheets[sheet_idx]['properties']['title']
            else:
                print("잘못된 입력입니다. 첫 번째 시트를 사용합니다.")
                sheet_name = sheets[0]['properties']['title']
        except ValueError:
            print("숫자를 입력하지 않았습니다. 첫 번째 시트를 사용합니다.")
            sheet_name = sheets[0]['properties']['title']
        
        # 파일명 입력 받기
        filename = input("\n저장할 JSON 파일 이름을 입력하세요 (기본: problems.json): ")
        if not filename:
            filename = "problems.json"
        if not filename.endswith('.json'):
            filename += '.json'
        
        # 데이터 가져오기
        print(f"\n{sheet_name} 시트에서 데이터를 가져오는 중...")
        problems = fetch_problems_from_sheet(service, sheet_name)
        
        if problems:
            # JSON 파일로 저장
            if save_to_json(problems, filename):
                print(f"\n변환 완료! {filename} 파일이 생성되었습니다.")
            else:
                print("\n파일 저장 중 오류가 발생했습니다.")
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