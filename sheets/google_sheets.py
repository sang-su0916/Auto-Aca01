import os
import sys

# 패키지 경로 추가
site_packages_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'google'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
]
for path in site_packages_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"Google API 모듈 임포트 오류: {e}")
    
    # 임시 대체 클래스
    class Credentials:
        @classmethod
        def from_service_account_file(cls, filename, scopes=None):
            return cls()
    
    class Service:
        def spreadsheets(self):
            return self
        
        def values(self):
            return self
        
        def get(self, **kwargs):
            return self
        
        def update(self, **kwargs):
            return self
        
        def append(self, **kwargs):
            return self
        
        def execute(self):
            return {"values": []}
    
    def build(api, version, credentials=None):
        return Service()
    
    class HttpError(Exception):
        pass

# 나머지 임포트
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