from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 나머지 임포트
import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GoogleSheetsAPI:
    def __init__(self):
        """Initialize Google Sheets API with credentials"""
        load_dotenv()
        
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SERVICE_ACCOUNT_FILE = 'credentials.json'
        self.SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        
        try:
            self.service = self._get_google_sheets_service()
            # Initialize headers if not already set
            self.initialize_headers()
            # Check if problems exist, if not, add sample problems
            self.ensure_sample_problems()
        except Exception as e:
            logger.error(f"Google Sheets API 초기화 오류: {e}")
            self.service = None
    
    def _get_google_sheets_service(self):
        credentials = Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        return service
    
    def initialize_headers(self):
        """Set up headers for both sheets if they don't exist"""
        problems_headers = [
            ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
             '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
        ]
        
        student_answers_headers = [
            ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
        ]
        
        # Update problems sheet headers
        self.write_range('problems!A1:N1', problems_headers)
        
        # Update student_answers sheet headers
        self.write_range('student_answers!A1:H1', student_answers_headers)

    def ensure_sample_problems(self):
        """샘플 문제 데이터가 없으면 추가합니다"""
        # 기존 문제 확인
        problems = self.get_problems()
        
        if not problems:
            logger.info("문제 데이터가 없습니다. 샘플 문제를 추가합니다.")
            sample_problems = [
                ['P001', '영어', '중3', '객관식', '중', 'What is the capital of the UK?', 
                 'London', 'Paris', 'Berlin', 'Rome', '', 'London', 'capital,UK,London', 
                 'The capital city of the United Kingdom is London.'],
                ['P002', '영어', '중3', '주관식', '중', 'Write a sentence using the word "beautiful".', 
                 '', '', '', '', '', 'The flower is beautiful.', 'beautiful,sentence', 
                 '주어와 동사를 포함한 완전한 문장이어야 합니다.'],
                ['P003', '영어', '중2', '객관식', '하', 'Which word is a verb?', 
                 'happy', 'book', 'run', 'fast', '', 'run', 'verb,part of speech', 
                 '동사(verb)는 행동이나 상태를 나타내는 품사입니다. run(달리다)은 동사입니다.'],
                ['P004', '영어', '고1', '객관식', '상', 'Choose the correct sentence.', 
                 'I have been to Paris last year.', 'I went to Paris last year.', 'I have went to Paris last year.', 'I go to Paris last year.', '', 
                 'I went to Paris last year.', 'grammar,past tense', '과거에 일어난 일에는 과거 시제(went)를 사용합니다.'],
                ['P005', '영어', '고2', '주관식', '중', 'What does "procrastination" mean?', 
                 '', '', '', '', '', 'Delaying or postponing tasks', 'vocabulary,meaning', 
                 'Procrastination은 일이나 활동을 미루는 행동을 의미합니다.'],
                ['P006', '영어', '중3', '객관식', '중', 'Which is NOT a fruit?', 
                 'Apple', 'Potato', 'Orange', 'Banana', '', 'Potato', 'vocabulary,food,category', 
                 'Potato(감자)는 채소(vegetable)입니다. 나머지는 모두 과일(fruit)입니다.'],
                ['P007', '영어', '고1', '주관식', '상', 'Translate: "그는 어제 도서관에서 책을 읽었다."', 
                 '', '', '', '', '', 'He read a book in the library yesterday.', 'translation,past tense', 
                 '과거 시제를 사용한 영어 문장으로 번역해야 합니다.'],
                ['P008', '영어', '중2', '객관식', '하', 'What time is it? (3:45)', 
                 'It\'s quarter to four.', 'It\'s quarter past three.', 'It\'s four forty-five.', 'It\'s three forty-five.', '', 
                 'It\'s quarter to four.', 'time,expression', '3:45는 "quarter to four"라고 표현합니다.'],
                ['P009', '영어', '고2', '객관식', '상', 'Which sentence uses the subjunctive mood correctly?', 
                 'If I was rich, I would buy a mansion.', 'If I were rich, I would buy a mansion.', 'If I am rich, I would buy a mansion.', 'If I will be rich, I would buy a mansion.', '', 
                 'If I were rich, I would buy a mansion.', 'grammar,subjunctive mood', '가정법 과거에서는 "were"를 모든 인칭에 사용합니다.'],
                ['P010', '영어', '중1', '주관식', '하', 'Count from 1 to 5 in English.', 
                 '', '', '', '', '', 'One, two, three, four, five', 'numbers,basic vocabulary', 
                 '영어로 1부터 5까지는 "one, two, three, four, five"입니다.']
            ]
            
            # 샘플 문제 추가
            self.write_range('problems!A2:N11', sample_problems)
            logger.info("샘플 문제 추가 완료")
    
    def write_range(self, range_name, values):
        """Write values to specified range in Google Sheets"""
        try:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body={'values': values}
            ).execute()
            logger.debug(f"Successfully wrote to range: {range_name}")
        except Exception as e:
            logger.error(f"Error writing to range {range_name}: {e}")
            raise
    
    def read_range(self, range_name):
        """Read values from specified range in Google Sheets"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name
            ).execute()
            return result.get('values', [])
        except Exception as e:
            logger.error(f"Error reading range {range_name}: {e}")
            raise
    
    def append_row(self, sheet_name, values):
        """Append a row to the specified sheet"""
        try:
            range_name = f'{sheet_name}!A:Z'  # Use full column range
            body = {
                'values': [values]
            }
            self.service.spreadsheets().values().append(
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            logger.debug(f"Successfully appended row to {sheet_name}")
        except Exception as e:
            logger.error(f"Error appending row to {sheet_name}: {e}")
            raise

    def create_spreadsheet(self, title: str) -> str:
        """Create a new spreadsheet with the specified title"""
        try:
            logger.debug(f"Creating spreadsheet with title: {title}")
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'problems'
                        }
                    },
                    {
                        'properties': {
                            'title': 'student_answers'
                        }
                    }
                ]
            }
            request = self.service.spreadsheets().create(body=spreadsheet)
            response = request.execute()
            logger.debug(f"Spreadsheet created with ID: {response['spreadsheetId']}")
            return response['spreadsheetId']
        except HttpError as e:
            logger.error(f"Error creating spreadsheet: {e}", exc_info=True)
            raise

    def append_values(self, range_name: str, values: List[List[Any]]) -> None:
        """Append values to the specified range"""
        try:
            logger.debug(f"Appending to range: {range_name}")
            body = {
                'values': values
            }
            self.service.spreadsheets().values().append(
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            logger.debug("Append successful")
        except HttpError as e:
            logger.error(f"Error appending values: {e}", exc_info=True)
            raise

    def clear_range(self, range_name: str) -> None:
        """Clear values in the specified range"""
        try:
            logger.debug(f"Clearing range: {range_name}")
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name
            ).execute()
            logger.debug("Clear successful")
        except HttpError as e:
            logger.error(f"Error clearing range: {e}", exc_info=True)
            raise

    def get_problems(self):
        """Get all problems from the problems sheet"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.SPREADSHEET_ID,
            range='problems!A2:N'
        ).execute()
        values = result.get('values', [])
        
        problems = []
        for row in values:
            if len(row) >= 12:  # Ensure we have at least the required fields
                problem = {
                    '문제ID': row[0],
                    '과목': row[1],
                    '학년': row[2],
                    '문제유형': row[3],
                    '난이도': row[4],
                    '문제내용': row[5],
                    '보기1': row[6],
                    '보기2': row[7],
                    '보기3': row[8],
                    '보기4': row[9],
                    '보기5': row[10],
                    '정답': row[11],
                    '키워드': row[12] if len(row) > 12 else '',
                    '해설': row[13] if len(row) > 13 else ''
                }
                problems.append(problem)
        return problems

    def submit_answer(self, student_id, name, grade, problem_id, answer):
        """Submit a student's answer to the student_answers sheet"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Find the correct answer from problems sheet
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.SPREADSHEET_ID,
            range='problems!A2:L'
        ).execute()
        problems = result.get('values', [])
        
        correct_answer = None
        for problem in problems:
            if problem[0] == problem_id:
                correct_answer = problem[11]
                break
        
        # Calculate score and feedback
        score = 100 if answer == correct_answer else 0
        feedback = '정답입니다!' if score == 100 else f'오답입니다. 정답은 {correct_answer}입니다.'
        
        # Append the answer to student_answers sheet
        values = [[student_id, name, grade, problem_id, answer, score, feedback, now]]
        self.service.spreadsheets().values().append(
            spreadsheetId=self.SPREADSHEET_ID,
            range='student_answers!A2:H',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': values}
        ).execute()
        
        return {
            'score': score,
            'feedback': feedback,
            'submitted_at': now
        }

    def get_student_results(self, student_name, student_id):
        # 임시 데이터 반환
        return [
            {
                "problem_id": 1,
                "score": 100,
                "feedback": "정답입니다!"
            }
        ]

    def get_statistics(self):
        # 임시 통계 데이터 반환
        return {
            "total_students": 1,
            "total_submissions": 1,
            "average_score": 90,
            "problem_stats": [
                {
                    "problem_id": 1,
                    "correct_ratio": 0.9
                }
            ]
        } 