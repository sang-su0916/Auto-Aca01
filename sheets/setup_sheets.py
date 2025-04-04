import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import logging
import random

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load credentials from the service account file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# The ID of your spreadsheet
SPREADSHEET_ID = '1hQc5KdnZJKXolGyK1ls1cjjlpLXHJ56S7kfw2M0SJi8'

def get_google_sheets_service():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    return service

def generate_sample_problems():
    # Sample vocabulary and grammar patterns for each grade
    grade_content = {
        '중1': {
            'vocabulary': ['book', 'pen', 'school', 'friend', 'teacher', 'student', 'computer', 'phone', 'desk', 'chair'],
            'patterns': ['What is this?', 'Where is the ~?', 'I am ~', 'You are ~', 'He/She is ~']
        },
        '중2': {
            'vocabulary': ['library', 'restaurant', 'hospital', 'airport', 'station', 'market', 'museum', 'park', 'hotel', 'bank'],
            'patterns': ['Can you ~?', 'Do you like ~?', 'What time ~?', 'How many ~?', 'Why do you ~?']
        },
        '중3': {
            'vocabulary': ['environment', 'technology', 'science', 'culture', 'history', 'society', 'economy', 'education', 'health', 'future'],
            'patterns': ['Have you ever ~?', 'What would you ~?', 'If I were ~', 'How long ~?', 'What makes you ~?']
        }
    }

    problems = []
    problem_id = 1

    for grade in ['중1', '중2', '중3']:
        for i in range(20):
            vocab = random.choice(grade_content[grade]['vocabulary'])
            pattern = random.choice(grade_content[grade]['patterns'])
            
            # Generate multiple choice question
            if i % 2 == 0:  # Vocabulary question
                question = f"다음 중 '{vocab}'의 뜻으로 가장 적절한 것은?"
                correct_answer = random.randint(1, 5)  # 1~5 중 정답 선택
                options = []
                for j in range(5):
                    if j + 1 == correct_answer:
                        options.append(get_korean_meaning(vocab))
                    else:
                        options.append(get_wrong_korean_meaning(vocab))
            else:  # Pattern question
                question = f"다음 문장 '{pattern}'을 활용한 올바른 표현은?"
                correct_answer = random.randint(1, 5)
                options = generate_pattern_options(pattern, vocab)

            problems.append([
                str(problem_id),  # 문제ID
                '영어',           # 과목
                grade,           # 학년
                '객관식',         # 문제유형
                ['하', '중', '상'][i % 3],  # 난이도
                question,        # 문제내용
                options[0],      # 보기1
                options[1],      # 보기2
                options[2],      # 보기3
                options[3],      # 보기4
                options[4],      # 보기5
                str(correct_answer),  # 정답
                vocab,           # 키워드
                f"이 문제는 {grade} {vocab}와(과) {pattern} 패턴을 학습하기 위한 문제입니다."  # 해설
            ])
            problem_id += 1

    return problems

def get_korean_meaning(word):
    meanings = {
        'book': '책', 'pen': '펜', 'school': '학교', 'friend': '친구', 'teacher': '선생님',
        'student': '학생', 'computer': '컴퓨터', 'phone': '전화기', 'desk': '책상', 'chair': '의자',
        'library': '도서관', 'restaurant': '식당', 'hospital': '병원', 'airport': '공항',
        'station': '역', 'market': '시장', 'museum': '박물관', 'park': '공원', 'hotel': '호텔',
        'bank': '은행', 'environment': '환경', 'technology': '기술', 'science': '과학',
        'culture': '문화', 'history': '역사', 'society': '사회', 'economy': '경제',
        'education': '교육', 'health': '건강', 'future': '미래'
    }
    return meanings.get(word, '알 수 없음')

def get_wrong_korean_meaning(word):
    all_meanings = list(set([meaning for meaning in {
        '책', '펜', '학교', '친구', '선생님', '학생', '컴퓨터', '전화기', '책상', '의자',
        '도서관', '식당', '병원', '공항', '역', '시장', '박물관', '공원', '호텔', '은행',
        '환경', '기술', '과학', '문화', '역사', '사회', '경제', '교육', '건강', '미래'
    } - {get_korean_meaning(word)}]))
    return random.choice(all_meanings)

def generate_pattern_options(pattern, vocab):
    base_options = [
        f"{pattern.replace('~', vocab)}",
        f"{pattern.replace('~', 'not ' + vocab)}",
        f"{pattern.replace('~', 'the ' + vocab)}",
        f"{pattern.replace('~', 'my ' + vocab)}",
        f"{pattern.replace('~', 'your ' + vocab)}"
    ]
    random.shuffle(base_options)
    return base_options

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

if __name__ == '__main__':
    setup_headers() 