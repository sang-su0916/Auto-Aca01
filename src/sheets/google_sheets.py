import os
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleSheetsManager:
    """
    Google Sheets 연동 및 관리를 위한 클래스
    학원 자동 첨삭 시스템에서 문제 및 학생 답안 데이터를 저장하고 조회합니다.
    """

    def __init__(self, credentials_path='credentials.json', spreadsheet_id=None):
        """
        Google Sheets API 클라이언트 초기화
        
        Args:
            credentials_path (str): Google API 인증 파일 경로
            spreadsheet_id (str): 사용할 Google 스프레드시트 ID
        """
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id or os.getenv('SPREADSHEET_ID')
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.service = None
        self._init_service()
        
    def _init_service(self):
        """Google Sheets API 서비스 초기화"""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=self.scopes
            )
            self.service = build('sheets', 'v4', credentials=creds)
            print("Google Sheets API 서비스 초기화 완료")
        except Exception as e:
            print(f"Google Sheets API 초기화 오류: {e}")
            self.service = None
    
    def create_spreadsheet(self, title="학원 자동 첨삭 시스템"):
        """
        새 스프레드시트 생성 및 기본 시트 구성
        
        Args:
            title (str): 새 스프레드시트 이름
            
        Returns:
            str: 생성된 스프레드시트 ID
        """
        if not self.service:
            print("서비스가 초기화되지 않았습니다.")
            return None
            
        try:
            # 스프레드시트 생성
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {'properties': {'title': 'problems'}},
                    {'properties': {'title': 'student_answers'}}
                ]
            }
            
            result = self.service.spreadsheets().create(body=spreadsheet).execute()
            self.spreadsheet_id = result['spreadsheetId']
            print(f"새 스프레드시트 생성 완료: {self.spreadsheet_id}")
            
            # 헤더 설정
            problems_header = [["문제ID", "문제", "난이도", "모범답안", "키워드"]]
            student_header = [["이름", "학번", "문제ID", "답안", "점수", "피드백", "제출시간"]]
            
            self.update_values('problems!A1:E1', problems_header)
            self.update_values('student_answers!A1:G1', student_header)
            
            return self.spreadsheet_id
            
        except HttpError as error:
            print(f"스프레드시트 생성 오류: {error}")
            return None
    
    def update_values(self, range_name, values):
        """
        지정된 범위에 데이터 업데이트
        
        Args:
            range_name (str): 시트 범위 (예: 'problems!A1:E10')
            values (list): 업데이트할 데이터 2D 리스트
            
        Returns:
            dict: API 응답 결과
        """
        if not self.service or not self.spreadsheet_id:
            print("서비스 또는 스프레드시트 ID가 설정되지 않았습니다.")
            return None
            
        try:
            body = {
                'values': values
            }
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            print(f"{result.get('updatedCells')} 셀 업데이트 완료")
            return result
        except HttpError as error:
            print(f"데이터 업데이트 오류: {error}")
            return None
    
    def get_values(self, range_name):
        """
        지정된 범위의 데이터 조회
        
        Args:
            range_name (str): 시트 범위 (예: 'problems!A2:E')
            
        Returns:
            list: 조회된 데이터 2D 리스트
        """
        if not self.service or not self.spreadsheet_id:
            print("서비스 또는 스프레드시트 ID가 설정되지 않았습니다.")
            return []
            
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return values
            
        except HttpError as error:
            print(f"데이터 조회 오류: {error}")
            return []
    
    def append_values(self, range_name, values):
        """
        지정된 범위 끝에 데이터 추가
        
        Args:
            range_name (str): 시트 범위 (예: 'student_answers!A:G')
            values (list): 추가할 데이터 2D 리스트
            
        Returns:
            dict: API 응답 결과
        """
        if not self.service or not self.spreadsheet_id:
            print("서비스 또는 스프레드시트 ID가 설정되지 않았습니다.")
            return None
            
        try:
            body = {
                'values': values
            }
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            print(f"데이터 추가 완료: {result.get('updates').get('updatedRows')} 행")
            return result
        except HttpError as error:
            print(f"데이터 추가 오류: {error}")
            return None
    
    def get_problems(self):
        """
        모든 문제 목록 조회
        
        Returns:
            list: 문제 데이터 리스트 (딕셔너리 형태)
        """
        data = self.get_values('problems!A2:E')
        if not data:
            return []
            
        problems = []
        for row in data:
            if len(row) >= 5:
                problem = {
                    "문제ID": row[0],
                    "문제": row[1],
                    "난이도": row[2],
                    "모범답안": row[3],
                    "키워드": row[4].split(',') if row[4] else []
                }
                problems.append(problem)
        
        return problems
    
    def get_student_answers(self, student_name=None, student_id=None):
        """
        학생 답안 조회 (전체 또는 특정 학생)
        
        Args:
            student_name (str, optional): 학생 이름으로 필터링
            student_id (str, optional): 학번으로 필터링
            
        Returns:
            list: 학생 답안 데이터 리스트
        """
        data = self.get_values('student_answers!A2:G')
        if not data:
            return []
            
        answers = []
        for row in data:
            if len(row) >= 6:
                answer = {
                    "이름": row[0],
                    "학번": row[1],
                    "문제ID": row[2],
                    "답안": row[3],
                    "점수": row[4] if len(row) > 4 else "",
                    "피드백": row[5] if len(row) > 5 else "",
                    "제출시간": row[6] if len(row) > 6 else ""
                }
                
                if (student_name and answer["이름"] != student_name) or \
                   (student_id and answer["학번"] != student_id):
                    continue
                    
                answers.append(answer)
        
        return answers
    
    def add_problem(self, problem_id, problem_text, difficulty, model_answer, keywords):
        """
        새 문제 추가
        
        Args:
            problem_id (str): 문제 ID
            problem_text (str): 문제 내용
            difficulty (str): 난이도
            model_answer (str): 모범답안
            keywords (list): 키워드 리스트
            
        Returns:
            bool: 성공 여부
        """
        keywords_str = ','.join(keywords) if isinstance(keywords, list) else keywords
        
        values = [[problem_id, problem_text, difficulty, model_answer, keywords_str]]
        result = self.append_values('problems!A:E', values)
        
        return result is not None
    
    def add_student_answer(self, name, student_id, problem_id, answer, score=None, feedback=None):
        """
        학생 답안 추가
        
        Args:
            name (str): 학생 이름
            student_id (str): 학번
            problem_id (str): 문제 ID
            answer (str): 학생 답안
            score (str, optional): 점수
            feedback (str, optional): 피드백
            
        Returns:
            bool: 성공 여부
        """
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        values = [[name, student_id, problem_id, answer, score or "", feedback or "", now]]
        result = self.append_values('student_answers!A:G', values)
        
        return result is not None
    
    def update_score_feedback(self, row_index, score, feedback):
        """
        학생 답안에 점수와 피드백 업데이트
        
        Args:
            row_index (int): 업데이트할 행 번호 (1부터 시작)
            score (str): 점수
            feedback (str): 피드백
            
        Returns:
            bool: 성공 여부
        """
        range_name = f'student_answers!E{row_index}:F{row_index}'
        values = [[score, feedback]]
        
        result = self.update_values(range_name, values)
        return result is not None

# 모듈 사용 예시
if __name__ == "__main__":
    # 환경 변수나 파일에서 스프레드시트 ID 로드
    # SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    
    # 또는 새 스프레드시트 생성
    sheets = GoogleSheetsManager()
    new_id = sheets.create_spreadsheet("학원 자동 첨삭 시스템")
    
    if new_id:
        print(f"새 스프레드시트 ID: {new_id}")
        # 환경 변수나 설정 파일에 ID 저장 권장 