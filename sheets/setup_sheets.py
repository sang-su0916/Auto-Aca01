import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import logging
import random
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load credentials from the service account file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# The ID of your spreadsheet
SPREADSHEET_ID = '1YcKaHcjnx5-WypEpYbcfg04s8TIq280l-gi6iISF5NQ'

def get_google_sheets_service():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    return service

def fetch_problems_from_sheet():
    """Google Sheets에서 문제 데이터를 가져옵니다"""
    try:
        service = get_google_sheets_service()
        
        # problems 시트에서 데이터 가져오기
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='problems!A2:N'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            logger.warning("No data found in Google Sheets.")
            return pd.DataFrame()
            
        # 데이터프레임 생성
        columns = ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                  '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
        
        problems = []
        for row in values:
            # 모든 열이 존재하는지 확인하고 없는 경우 빈 문자열 추가
            row_extended = row + [''] * (len(columns) - len(row))
            problem = dict(zip(columns, row_extended[:len(columns)]))
            problems.append(problem)
            
        return pd.DataFrame(problems)
        
    except Exception as e:
        logger.error(f"Error fetching problems from Google Sheets: {e}")
        return pd.DataFrame()

def generate_sample_problems():
    """각 학년별 20문제씩 샘플 문제를 생성합니다"""
    all_problems = []
    
    # 중1 문제 (20문제)
    for i in range(1, 21):
        problem = [
            f'P{i:03d}',  # 문제ID
            '영어',         # 과목
            '중1',         # 학년
            '객관식' if i % 3 != 0 else '주관식',  # 문제유형
            '중' if i % 3 == 0 else ('상' if i % 3 == 1 else '하'),  # 난이도
            f'중1 영어 문제 {i}: Which of the following is a fruit?',  # 문제내용
            'Apple' if i % 5 == 0 else 'Car',  # 보기1
            'Banana' if i % 5 == 1 else 'House',  # 보기2
            'Orange' if i % 5 == 2 else 'Book',  # 보기3
            'Strawberry' if i % 5 == 3 else 'Pen',  # 보기4
            'Grape' if i % 5 == 4 else '',  # 보기5
            ['Apple', 'Banana', 'Orange', 'Strawberry', 'Grape'][i % 5],  # 정답
            'fruit,food',  # 키워드
            f'The correct answer is {["Apple", "Banana", "Orange", "Strawberry", "Grape"][i % 5]} because it is a fruit.'  # 해설
        ]
        all_problems.append(problem)
    
    # 중2 문제 (20문제)
    for i in range(21, 41):
        problem = [
            f'P{i:03d}',  # 문제ID
            '영어',         # 과목
            '중2',         # 학년
            '객관식' if i % 3 != 0 else '주관식',  # 문제유형
            '중' if i % 3 == 0 else ('상' if i % 3 == 1 else '하'),  # 난이도
            f'중2 영어 문제 {i-20}: What time is it?',  # 문제내용
            '2:30' if i % 5 == 0 else '3:15',  # 보기1
            '4:45' if i % 5 == 1 else '1:00',  # 보기2
            '7:20' if i % 5 == 2 else '9:10',  # 보기3
            '10:55' if i % 5 == 3 else '12:05',  # 보기4
            '6:40' if i % 5 == 4 else '',  # 보기5
            ['2:30', '4:45', '7:20', '10:55', '6:40'][i % 5],  # 정답
            'time,clock,hour',  # 키워드
            f'The correct time is {["2:30", "4:45", "7:20", "10:55", "6:40"][i % 5]}.'  # 해설
        ]
        all_problems.append(problem)
    
    # 중3 문제 (20문제)
    for i in range(41, 61):
        problem = [
            f'P{i:03d}',  # 문제ID
            '영어',         # 과목
            '중3',         # 학년
            '객관식' if i % 3 != 0 else '주관식',  # 문제유형
            '중' if i % 3 == 0 else ('상' if i % 3 == 1 else '하'),  # 난이도
            f'중3 영어 문제 {i-40}: Which word is a verb?',  # 문제내용
            'Run' if i % 5 == 0 else 'Book',  # 보기1
            'Jump' if i % 5 == 1 else 'Table',  # 보기2
            'Swim' if i % 5 == 2 else 'Pen',  # 보기3
            'Dance' if i % 5 == 3 else 'Chair',  # 보기4
            'Read' if i % 5 == 4 else '',  # 보기5
            ['Run', 'Jump', 'Swim', 'Dance', 'Read'][i % 5],  # 정답
            'verb,action',  # 키워드
            f'{["Run", "Jump", "Swim", "Dance", "Read"][i % 5]} is a verb because it describes an action.'  # 해설
        ]
        all_problems.append(problem)
    
    return all_problems

def setup_headers():
    service = get_google_sheets_service()
    sheets = service.spreadsheets()

    # Define headers for both sheets
    problems_headers = [
        ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
         '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
    ]
    
    student_answers_headers = [
        ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
    ]

    try:
        # Update problems sheet headers
        sheets.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='problems!A1:N1',
            valueInputOption='RAW',
            body={'values': problems_headers}
        ).execute()
        print("Successfully updated problems sheet headers")

        # Generate and add sample problems
        sample_problems = generate_sample_problems()
        sheets.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='problems!A2:N61',  # 60 problems (20 per grade)
            valueInputOption='RAW',
            body={'values': sample_problems}
        ).execute()
        print("Successfully added sample problems")

        # Update student_answers sheet headers
        sheets.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='student_answers!A1:H1',
            valueInputOption='RAW',
            body={'values': student_answers_headers}
        ).execute()
        print("Successfully updated student_answers sheet headers")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    setup_headers()
    print("Google Sheets setup completed successfully!") 