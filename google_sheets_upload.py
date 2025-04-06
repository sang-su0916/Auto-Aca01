import gspread
import os
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime

# 스프레드시트 ID 설정
SPREADSHEET_ID = '1YcKaHcjnx5-WypEpYbcfg04s8TIq280l-gi6iISF5NQ'

def setup_google_sheets():
    """Google Sheets API 초기화 및 연결 확인"""
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    try:
        # 서비스 계정을 통한 인증
        credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        client = gspread.authorize(credentials)
        
        # 스프레드시트 열기
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        print(f"연결 성공! 스프레드시트 제목: {spreadsheet.title}")
        return spreadsheet
    except Exception as e:
        print(f"Google Sheets 연결 오류: {str(e)}")
        return None

def generate_sample_problems():
    """각 학년별 20문제씩 샘플 문제를 생성합니다"""
    all_problems = []
    
    # 중1 문제 (20문제)
    for i in range(1, 21):
        problem = {
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중1',
            '문제유형': '객관식' if i % 3 != 0 else '주관식',
            '난이도': '중' if i % 3 == 0 else ('상' if i % 3 == 1 else '하'),
            '문제내용': f'중1 영어 문제 {i}: Which of the following is a fruit?',
            '보기1': 'Apple' if i % 5 == 0 else 'Car',
            '보기2': 'Banana' if i % 5 == 1 else 'House',
            '보기3': 'Orange' if i % 5 == 2 else 'Book',
            '보기4': 'Strawberry' if i % 5 == 3 else 'Pen',
            '보기5': 'Grape' if i % 5 == 4 else '',
            '정답': ['Apple', 'Banana', 'Orange', 'Strawberry', 'Grape'][i % 5],
            '키워드': 'fruit,food',
            '해설': f'The correct answer is {["Apple", "Banana", "Orange", "Strawberry", "Grape"][i % 5]} because it is a fruit.'
        }
        all_problems.append(problem)
    
    # 중2 문제 (20문제)
    for i in range(21, 41):
        problem = {
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중2',
            '문제유형': '객관식' if i % 3 != 0 else '주관식',
            '난이도': '중' if i % 3 == 0 else ('상' if i % 3 == 1 else '하'),
            '문제내용': f'중2 영어 문제 {i-20}: What time is it?',
            '보기1': '2:30' if i % 5 == 0 else '3:15',
            '보기2': '4:45' if i % 5 == 1 else '1:00',
            '보기3': '7:20' if i % 5 == 2 else '9:10',
            '보기4': '10:55' if i % 5 == 3 else '12:05',
            '보기5': '6:40' if i % 5 == 4 else '',
            '정답': ['2:30', '4:45', '7:20', '10:55', '6:40'][i % 5],
            '키워드': 'time,clock,hour',
            '해설': f'The correct time is {["2:30", "4:45", "7:20", "10:55", "6:40"][i % 5]}.'
        }
        all_problems.append(problem)
    
    # 중3 문제 (20문제)
    for i in range(41, 61):
        problem = {
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중3',
            '문제유형': '객관식' if i % 3 != 0 else '주관식',
            '난이도': '중' if i % 3 == 0 else ('상' if i % 3 == 1 else '하'),
            '문제내용': f'중3 영어 문제 {i-40}: Which word is a verb?',
            '보기1': 'Run' if i % 5 == 0 else 'Book',
            '보기2': 'Jump' if i % 5 == 1 else 'Table',
            '보기3': 'Swim' if i % 5 == 2 else 'Pen',
            '보기4': 'Dance' if i % 5 == 3 else 'Chair',
            '보기5': 'Read' if i % 5 == 4 else '',
            '정답': ['Run', 'Jump', 'Swim', 'Dance', 'Read'][i % 5],
            '키워드': 'verb,action',
            '해설': f'{["Run", "Jump", "Swim", "Dance", "Read"][i % 5]} is a verb because it describes an action.'
        }
        all_problems.append(problem)
    
    return all_problems

def setup_headers_and_sample_data():
    """스프레드시트에 헤더와 샘플 데이터 설정"""
    spreadsheet = setup_google_sheets()
    if not spreadsheet:
        return False
    
    try:
        # 기존 시트 확인 및 생성
        sheet_names = [sheet.title for sheet in spreadsheet.worksheets()]
        
        # problems 시트 설정
        if 'problems' not in sheet_names:
            problems_sheet = spreadsheet.add_worksheet(title='problems', rows=100, cols=20)
            print("problems 시트가 생성되었습니다.")
        else:
            problems_sheet = spreadsheet.worksheet('problems')
            print("기존 problems 시트를 사용합니다.")
        
        # student_answers 시트 설정
        if 'student_answers' not in sheet_names:
            student_sheet = spreadsheet.add_worksheet(title='student_answers', rows=100, cols=20)
            print("student_answers 시트가 생성되었습니다.")
        else:
            student_sheet = spreadsheet.worksheet('student_answers')
            print("기존 student_answers 시트를 사용합니다.")
        
        # 헤더 설정
        problems_headers = [
            '문제ID', '과목', '학년', '문제유형', '난이도', '문제내용',
            '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설'
        ]
        
        student_headers = [
            '학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간'
        ]
        
        # problems 시트 헤더 설정
        problems_sheet.update('A1:N1', [problems_headers])
        print("problems 시트 헤더가 설정되었습니다.")
        
        # student_answers 시트 헤더 설정
        student_sheet.update('A1:H1', [student_headers])
        print("student_answers 시트 헤더가 설정되었습니다.")
        
        # 샘플 문제 생성
        sample_problems = generate_sample_problems()
        
        # 샘플 문제를 DataFrame으로 변환
        df = pd.DataFrame(sample_problems)
        
        # DataFrame을 리스트로 변환하여 시트에 업로드
        values = [df.columns.tolist()] + df.values.tolist()
        problems_sheet.clear()  # 기존 데이터 지우기
        problems_sheet.update('A1', values)
        
        print(f"총 {len(sample_problems)}개의 샘플 문제가 업로드되었습니다.")
        return True
        
    except Exception as e:
        print(f"스프레드시트 설정 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"Google Sheets ID: {SPREADSHEET_ID}")
    if setup_headers_and_sample_data():
        print("Google Sheets 설정이 완료되었습니다!")
        print(f"스프레드시트 URL: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
    else:
        print("Google Sheets 설정 중 오류가 발생했습니다.") 