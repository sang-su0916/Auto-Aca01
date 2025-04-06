import os
import sys
import traceback
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Make sure the needed packages are installed
# pip install pandas python-dotenv google-auth google-api-python-client

# 환경 변수 로드
load_dotenv()

# 상수 정의
SHEETS_AVAILABLE = True  # 이제 항상 사용 가능하도록 설정
SERVICE_ACCOUNT_FILE = '../credentials.json'  # 상위 디렉토리에 있는 credentials.json 파일 참조
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0')

def get_sheets_service():
    """Google Sheets API 서비스 객체 반환"""
    try:
        # 인증 정보 생성
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # 서비스 객체 생성
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"Google Sheets API 초기화 오류: {str(e)}")
        traceback.print_exc()
        return None

def fetch_problems_from_sheet():
    """Google Sheets에서 문제 데이터 가져오기"""
    service = get_sheets_service()
    if not service:
        print("Google Sheets 서비스를 초기화할 수 없습니다.")
        return pd.DataFrame()
    
    try:
        # 스프레드시트 정보 가져오기
        spreadsheet_info = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID).execute()
        
        # 시트 목록 확인
        sheets = spreadsheet_info.get('sheets', [])
        sheet_titles = [sheet['properties']['title'] for sheet in sheets]
        
        # 데이터 가져오기
        sheet_range = None
        if '테스트 데이터' in sheet_titles:
            sheet_range = '테스트 데이터!A:N'  # 테스트 데이터 시트
        else:
            sheet_range = 'Sheet1!A:N'  # 기본 시트
            
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=sheet_range
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("스프레드시트에 데이터가 없습니다.")
            # 헤더만 있는 경우 빈 데이터프레임 반환
            if len(values) <= 1:
                return pd.DataFrame()
                
            # 헤더만 가져오고 데이터는 없는 경우
            headers = values[0]
            return pd.DataFrame(columns=headers)
        
        # 헤더 가져오기
        headers = values[0]
        
        # 데이터 가져오기 (헤더 제외)
        data = values[1:]
        
        # 누락된 필드 채우기
        for row in data:
            while len(row) < len(headers):
                row.append('')
                
        # 데이터프레임 생성
        df = pd.DataFrame(data, columns=headers)
        print(f"Google Sheets에서 {len(df)}개의 문제를 가져왔습니다.")
        return df
        
    except HttpError as error:
        print(f"Google Sheets API 오류: {error}")
        return pd.DataFrame()
    except Exception as e:
        print(f"문제 데이터 가져오기 오류: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()

def initialize_sheets():
    """초기 시트 설정 및 데이터 추가"""
    service = get_sheets_service()
    if not service:
        print("Google Sheets 서비스를 초기화할 수 없습니다.")
        return False
    
    try:
        # 스프레드시트 정보 가져오기
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID).execute()
            
        # 시트 목록 확인
        sheets = spreadsheet.get('sheets', [])
        sheet_titles = [sheet['properties']['title'] for sheet in sheets]
        
        # 첫 번째 시트의 헤더 설정
        sheet_name = '테스트 데이터'
        range_name = f'{sheet_name}!A1:N1'
        
        # 시트 이름이 이미 '테스트 데이터'가 아니라면 이름 변경
        if '테스트 데이터' not in sheet_titles:
            # 첫 번째 시트의 ID 가져오기
            first_sheet_id = sheets[0]['properties']['sheetId']
            
            # 시트 이름 변경 요청
            request = {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': first_sheet_id,
                        'title': sheet_name
                    },
                    'fields': 'title'
                }
            }
            
            # 배치 업데이트 실행
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body={'requests': [request]}
            ).execute()
            
            print(f"시트 이름을 '{sheet_name}'으로 변경했습니다.")
        
        headers = [
            ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
             '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
        ]
        
        # 헤더 업데이트
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body={'values': headers}
        ).execute()
        
        # 샘플 데이터 추가
        sample_data = []
        subjects = ["영어", "수학", "국어", "과학", "사회"]
        grades = ["중1", "중2", "중3", "고1", "고2", "고3"]
        difficulties = ["상", "중", "하"]
        problem_types = ["객관식", "주관식"]
        
        for i in range(1, 21):
            subject = subjects[i % len(subjects)]
            grade = grades[i % len(grades)]
            difficulty = difficulties[i % len(difficulties)]
            problem_type = problem_types[i % len(problem_types)]
            
            if problem_type == "객관식":
                sample_data.append([
                    f'P{i:03d}',
                    subject,
                    grade,
                    problem_type,
                    difficulty,
                    f'샘플 {subject} 문제 {i}번입니다. 올바른 답을 고르세요.',
                    '보기 1',
                    '보기 2',
                    '보기 3',
                    '보기 4',
                    '',
                    '1',
                    '',
                    f'샘플 문제 {i}번의 해설입니다.'
                ])
            else:
                sample_data.append([
                    f'P{i:03d}',
                    subject,
                    grade,
                    problem_type,
                    difficulty,
                    f'샘플 {subject} 주관식 문제 {i}번입니다. 답을 작성하세요.',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '정답',
                    '키워드1,키워드2',
                    f'샘플 주관식 문제 {i}번의 해설입니다.'
                ])
        
        # 샘플 데이터 추가
        if sample_data:
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range='테스트 데이터!A2:N',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': sample_data}
            ).execute()
            
            print(f"스프레드시트에 {len(sample_data)}개의 샘플 문제가 추가되었습니다.")
            
        return True
    except Exception as e:
        print(f"시트 초기화 오류: {str(e)}")
        traceback.print_exc()
        return False

# 스크립트가 직접 실행될 때 초기화 수행
if __name__ == "__main__":
    initialize_sheets() 