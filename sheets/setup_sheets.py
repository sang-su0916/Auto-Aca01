import os
import sys
import traceback
from dotenv import load_dotenv
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# .env 파일 로드
load_dotenv()

# 상수 정의
SHEETS_AVAILABLE = True  # 이제 항상 사용 가능하도록 설정
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID', '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0')

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
        # 데이터 가져오기
        sheet_range = 'problems!A2:N'
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=sheet_range
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("스프레드시트에 데이터가 없습니다.")
            return pd.DataFrame()
        
        # 데이터 프레임 생성
        columns = ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                  '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
        
        # 누락된 필드 채우기
        for row in values:
            while len(row) < len(columns):
                row.append('')
                
        # 데이터프레임 생성
        df = pd.DataFrame(values, columns=columns)
        print(f"Google Sheets에서 {len(df)}개의 문제를 가져왔습니다.")
        return df
        
    except HttpError as error:
        print(f"Google Sheets API 오류: {error}")
        return pd.DataFrame()
    except Exception as e:
        print(f"문제 데이터 가져오기 오류: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()

def save_student_answer(student_id, name, grade, problem_id, answer, score, feedback):
    """학생 답변을 Google Sheets에 저장"""
    service = get_sheets_service()
    if not service:
        print("Google Sheets 서비스를 초기화할 수 없습니다.")
        return False
    
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # 데이터 저장
        values = [[student_id, name, grade, problem_id, answer, score, feedback, now]]
        body = {'values': values}
        
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='student_answers!A2:H',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        print(f"학생 답변이 저장되었습니다: {result.get('updates').get('updatedRows')}행 추가됨")
        return True
        
    except Exception as e:
        print(f"학생 답변 저장 오류: {str(e)}")
        traceback.print_exc()
        return False

class GoogleSheetsSetup:
    """Google Sheets 설정 클래스"""
    def __init__(self):
        self.service = get_sheets_service()
        
    def initialize_sheets(self):
        """필요한 시트 초기화"""
        if not self.service:
            print("Google Sheets 서비스를 초기화할 수 없습니다.")
            return False
            
        try:
            # 스프레드시트 정보 가져오기
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=SPREADSHEET_ID).execute()
                
            # 시트 목록 확인
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            print(f"기존 시트: {existing_sheets}")
            
            # 필요한 시트 생성
            required_sheets = ['problems', 'student_answers']
            for sheet_name in required_sheets:
                if sheet_name not in existing_sheets:
                    self.create_sheet(sheet_name)
                    
            # 헤더 설정
            self.set_headers()
            
            # 샘플 문제 추가
            self.add_sample_problems()
            
            return True
        except Exception as e:
            print(f"시트 초기화 오류: {str(e)}")
            traceback.print_exc()
            return False
            
    def create_sheet(self, sheet_name):
        """새 시트 생성"""
        try:
            request = {
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }
            
            body = {'requests': [request]}
            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=body
            ).execute()
            
            print(f"시트 생성 완료: {sheet_name}")
            return True
        except Exception as e:
            print(f"시트 생성 오류: {str(e)}")
            return False
            
    def set_headers(self):
        """시트에 헤더 설정"""
        try:
            # problems 시트 헤더
            problems_headers = [
                ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                 '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
            ]
            
            # student_answers 시트 헤더
            student_answers_headers = [
                ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
            ]
            
            # 헤더 업데이트
            self.service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range='problems!A1:N1',
                valueInputOption='RAW',
                body={'values': problems_headers}
            ).execute()
            
            self.service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range='student_answers!A1:H1',
                valueInputOption='RAW',
                body={'values': student_answers_headers}
            ).execute()
            
            print("헤더 설정 완료")
            return True
        except Exception as e:
            print(f"헤더 설정 오류: {str(e)}")
            return False
            
    def add_sample_problems(self):
        """샘플 문제 추가"""
        try:
            # 기존 문제 확인
            result = self.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range='problems!A2:A'
            ).execute()
            
            values = result.get('values', [])
            if values and len(values) > 10:
                print(f"이미 {len(values)}개의 문제가 있습니다. 샘플 추가를 건너뜁니다.")
                return True
                
            # 샘플 문제 생성
            sample_problems = []
            
            # 학년별로 문제 생성
            grades = ['중1', '중2', '중3', '고1', '고2', '고3']
            
            for grade_idx, grade in enumerate(grades):
                # 학년별 40문제 (총 240문제)
                for i in range(1, 41):
                    problem_id = f"{grade}-{i:03d}"
                    subject = "영어" if i <= 20 else "수학"
                    problem_type = "객관식" if i % 5 != 0 else "주관식"
                    difficulty = ((i-1) % 5) + 1  # 1~5 난이도
                    
                    if subject == "영어":
                        content = f"{grade} {subject} 샘플 문제 {i}. 다음 중 올바른 문장을 고르시오."
                        options = [
                            f"보기 {j+1}: 예시 보기 문장입니다." for j in range(5)
                        ]
                        answer = str((i % 5) + 1)
                        keywords = "샘플, 영어, 문법"
                        explanation = f"해설: {answer}번이 올바른 문장입니다. 그 이유는..."
                    else:
                        content = f"{grade} {subject} 샘플 문제 {i}. 다음 방정식을 푸시오: 2x + {i} = {i*2}"
                        options = [
                            f"{j*i/2}" for j in range(5)
                        ]
                        answer = "2" if problem_type == "주관식" else str((i % 5) + 1)
                        keywords = "샘플, 수학, 방정식"
                        explanation = f"해설: 2x + {i} = {i*2}이므로, 2x = {i}, x = {i/2}입니다."
                    
                    row = [
                        problem_id, subject, grade, problem_type, str(difficulty),
                        content, options[0], options[1], options[2], options[3], options[4],
                        answer, keywords, explanation
                    ]
                    sample_problems.append(row)
            
            # 데이터 추가
            self.service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range='problems!A2',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': sample_problems}
            ).execute()
            
            print(f"{len(sample_problems)}개의 샘플 문제 추가 완료")
            return True
        except Exception as e:
            print(f"샘플 문제 추가 오류: {str(e)}")
            traceback.print_exc()
            return False

    def ensure_sheets_exist(self):
        """필요한 시트들이 존재하는지 확인하고 없으면 생성"""
        if not self.service:
            print("Google Sheets 서비스를 초기화할 수 없습니다.")
            return False
            
        try:
            # 스프레드시트 정보 가져오기
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=SPREADSHEET_ID).execute()
                
            # 시트 목록 확인
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            print(f"기존 시트: {existing_sheets}")
            
            # 필요한 시트 생성
            required_sheets = ['problems', 'student_answers']
            missing_sheets = []
            
            for sheet_name in required_sheets:
                if sheet_name not in existing_sheets:
                    missing_sheets.append(sheet_name)
                    
            if missing_sheets:
                print(f"없는 시트를 생성합니다: {missing_sheets}")
                for sheet_name in missing_sheets:
                    self.create_sheet(sheet_name)
                # 헤더 설정
                self.set_headers()
            else:
                print("모든 필요한 시트가 이미 존재합니다.")
                
            return True
        except Exception as e:
            print(f"시트 확인 오류: {str(e)}")
            traceback.print_exc()
            return False 