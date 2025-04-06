#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import random
from typing import List, Any
import traceback
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('google_sheets_api')

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    logger.error("Google API 관련 패키지가 설치되지 않았습니다.")

class GoogleSheetsAPI:
    """Google Sheets API 연동 클래스"""
    
    def __init__(self):
        """초기화 및 API 서비스 생성"""
        # 상수 정의
        self.credentials_file = os.path.abspath('credentials.json')
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        
        # 스프레드시트 ID
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        
        # 로그 출력
        logging.info(f"초기화: 인증 파일 경로 = {self.credentials_file}, 스프레드시트 ID = {self.spreadsheet_id}")
        logging.info(f"인증 파일 존재 여부: {os.path.exists(self.credentials_file)}")
        logging.info(f"환경 변수 설정 여부: {self.spreadsheet_id is not None}")
        
        # API 서비스 초기화
        self.service = self._create_service()
    
    def _create_service(self):
        """Google Sheets API 서비스 객체 생성"""
        try:
            # 인증 정보 파일 확인
            if not os.path.exists(self.credentials_file):
                logger.error(f"오류: {self.credentials_file} 파일을 찾을 수 없습니다.")
                return None
            
            logger.info(f"인증 파일 경로: {self.credentials_file}")
            
            # 인증 정보 생성
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=self.scopes)
            
            # 서비스 객체 생성
            service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets API 서비스가 성공적으로 초기화되었습니다.")
            return service
        except Exception as e:
            logger.error(f"Google Sheets API 초기화 오류: {str(e)}")
            traceback.print_exc()
            return None
    
    def is_connected(self):
        """API 연결 상태 확인"""
        try:
            if self.service is None or self.spreadsheet_id is None:
                logger.warning("API 서비스 또는 스프레드시트 ID가 설정되지 않았습니다.")
                return False
                
            # 스프레드시트 정보 요청으로 연결 확인
            self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            logger.info("Google Sheets API 연결이 확인되었습니다.")
            return True
        except Exception as e:
            logger.error(f"Google Sheets API 연결 확인 오류: {str(e)}")
            return False
    
    def test_connection(self):
        """연결 테스트"""
        try:
            if not self.is_connected():
                logger.warning("Google Sheets API가 초기화되지 않았습니다.")
                return False
            
            # 스프레드시트 정보 가져오기
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id).execute()
            
            logger.info(f"연결 성공! 스프레드시트 타이틀: '{spreadsheet['properties']['title']}'")
            return True
        except Exception as e:
            logger.error(f"연결 테스트 실패: {str(e)}")
            return False
    
    def fetch_problems(self, sheet_name='테스트 데이터'):
        """문제 데이터 가져오기"""
        if not self.is_connected():
            print("Google Sheets API가 초기화되지 않았습니다.")
            return pd.DataFrame()
        
        try:
            # 데이터 가져오기
            range_name = f'{sheet_name}!A:N'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print("스프레드시트에 데이터가 없습니다.")
                return pd.DataFrame()
            
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
    
    def update_problem(self, problem_id, data, sheet_name='테스트 데이터'):
        """문제 데이터 업데이트"""
        if not self.is_connected():
            print("Google Sheets API가 초기화되지 않았습니다.")
            return False
        
        try:
            # 현재 데이터 가져오기
            range_name = f'{sheet_name}!A:N'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print("스프레드시트에 데이터가 없습니다.")
                return False
            
            # 헤더 가져오기
            headers = values[0]
            
            # 문제 ID로 행 찾기
            row_index = -1
            for i, row in enumerate(values):
                if i > 0 and row and row[0] == problem_id:
                    row_index = i
                    break
            
            if row_index == -1:
                print(f"문제 ID '{problem_id}'를 찾을 수 없습니다.")
                return False
            
            # 업데이트할 행 데이터 준비
            update_row = []
            for field in headers:
                if field in data:
                    update_row.append(data[field])
                else:
                    # 원래 값 유지
                    original_index = headers.index(field)
                    update_row.append(values[row_index][original_index] if original_index < len(values[row_index]) else '')
            
            # 데이터 업데이트
            update_range = f'{sheet_name}!A{row_index+1}:{chr(65+len(headers)-1)}{row_index+1}'
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=update_range,
                valueInputOption='RAW',
                body={'values': [update_row]}
            ).execute()
            
            print(f"문제 ID '{problem_id}'가 업데이트되었습니다.")
            return True
        except Exception as e:
            print(f"문제 업데이트 오류: {str(e)}")
            traceback.print_exc()
            return False
    
    def add_problem(self, data, sheet_name='테스트 데이터'):
        """새 문제 추가"""
        if not self.is_connected():
            print("Google Sheets API가 초기화되지 않았습니다.")
            return False
        
        try:
            # 현재 데이터 가져오기
            range_name = f'{sheet_name}!A:N'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print("스프레드시트에 데이터가 없습니다.")
                return False
            
            # 헤더 가져오기
            headers = values[0]
            
            # 추가할 행 데이터 준비
            new_row = []
            for field in headers:
                new_row.append(data.get(field, ''))
            
            # 데이터 추가
            append_range = f'{sheet_name}!A:N'
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=append_range,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [new_row]}
            ).execute()
            
            print(f"새 문제가 추가되었습니다. ID: {data.get('문제ID', '알 수 없음')}")
            return True
        except Exception as e:
            print(f"문제 추가 오류: {str(e)}")
            traceback.print_exc()
            return False
    
    def delete_problem(self, problem_id, sheet_name='테스트 데이터'):
        """문제 삭제"""
        if not self.is_connected():
            print("Google Sheets API가 초기화되지 않았습니다.")
            return False
        
        try:
            # 현재 데이터 가져오기
            range_name = f'{sheet_name}!A:N'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print("스프레드시트에 데이터가 없습니다.")
                return False
            
            # 문제 ID로 행 찾기
            row_index = -1
            for i, row in enumerate(values):
                if i > 0 and row and row[0] == problem_id:
                    row_index = i
                    break
            
            if row_index == -1:
                print(f"문제 ID '{problem_id}'를 찾을 수 없습니다.")
                return False
            
            # 시트 ID 가져오기
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id).execute()
            sheet_id = None
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                print(f"시트 '{sheet_name}'을 찾을 수 없습니다.")
                return False
            
            # 행 삭제 요청
            request = {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': row_index,
                        'endIndex': row_index + 1
                    }
                }
            }
            
            # 요청 실행
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': [request]}
            ).execute()
            
            print(f"문제 ID '{problem_id}'가 삭제되었습니다.")
            return True
        except Exception as e:
            print(f"문제 삭제 오류: {str(e)}")
            traceback.print_exc()
            return False

    def get_problems(self):
        """문제 목록 가져오기"""
        try:
            # API 호출하여 problems 시트의 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, 
                range='problems!A2:N'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("문제가 없거나 가져올 수 없습니다.")
                return []
            
            # 열 이름 가져오기
            header_result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, 
                range='problems!A1:N1'
            ).execute()
            
            headers = header_result.get('values', [['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                                                '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']])[0]
            
            # 데이터 처리 - 각 행을 사전 형태로 변환
            problems = []
            for row in values:
                # 부족한 열은 빈 문자열로 채우기
                if len(row) < len(headers):
                    row.extend([''] * (len(headers) - len(row)))
                
                # 문제 데이터 생성
                problem_data = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        problem_data[header] = row[i]
                    else:
                        problem_data[header] = ''
                
                problems.append(problem_data)
            
            logger.info(f"총 {len(problems)}개의 문제를 성공적으로 가져왔습니다.")
            return problems
        except HttpError as error:
            logger.error(f"문제 가져오기 API 오류: {error}")
            raise
        except Exception as e:
            logger.error(f"문제 가져오기 중 오류 발생: {str(e)}")
            raise
    
    def get_student_answers(self):
        """학생 답변 가져오기"""
        try:
            # API 호출하여 student_answers 시트의 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, 
                range='student_answers!A2:H'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("학생 답변이 없거나 가져올 수 없습니다.")
                return []
            
            # 열 이름 가져오기
            header_result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, 
                range='student_answers!A1:H1'
            ).execute()
            
            headers = header_result.get('values', [['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']])[0]
            
            # 데이터 처리 - 각 행을 사전 형태로 변환
            answers = []
            for row in values:
                # 부족한 열은 빈 문자열로 채우기
                if len(row) < len(headers):
                    row.extend([''] * (len(headers) - len(row)))
                
                # 답변 데이터 생성
                answer_data = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        # 점수는 숫자로 변환
                        if header == '점수' and row[i]:
                            try:
                                answer_data[header] = float(row[i])
                            except ValueError:
                                answer_data[header] = 0
                        else:
                            answer_data[header] = row[i]
                    else:
                        answer_data[header] = ''
                
                answers.append(answer_data)
            
            logger.info(f"총 {len(answers)}개의 학생 답변을 성공적으로 가져왔습니다.")
            return answers
        except HttpError as error:
            logger.error(f"학생 답변 가져오기 API 오류: {error}")
            raise
        except Exception as e:
            logger.error(f"학생 답변 가져오기 중 오류 발생: {str(e)}")
            raise
    
    def add_student_answer(self, answer_data):
        """학생 답변 추가하기"""
        try:
            # 답변 데이터 추출 (키 순서가 중요)
            headers = ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
            
            values = []
            for header in headers:
                values.append(str(answer_data.get(header, '')))
            
            # API 호출하여 student_answers 시트에 행 추가
            body = {
                'values': [values]
            }
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='student_answers!A2:H',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"학생 '{answer_data['이름']}'의 문제 '{answer_data['문제ID']}' 답변이 성공적으로 추가되었습니다.")
            return result
        except HttpError as error:
            logger.error(f"학생 답변 추가 API 오류: {error}")
            raise
        except Exception as e:
            logger.error(f"학생 답변 추가 중 오류 발생: {str(e)}")
            raise

    def clear_range(self, range_name):
        """시트의 특정 범위 데이터 지우기"""
        try:
            result = self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            logger.info(f"범위 '{range_name}'의 데이터가 성공적으로 지워졌습니다.")
            return result
        except HttpError as error:
            logger.error(f"데이터 지우기 API 오류: {error}")
            raise
        except Exception as e:
            logger.error(f"데이터 지우기 중 오류 발생: {str(e)}")
            raise

    def append_row(self, sheet_name, row_data):
        """시트에 행 추가하기"""
        try:
            # API 호출하여 시트에 행 추가
            body = {
                'values': [row_data]
            }
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f'{sheet_name}!A1',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"시트 '{sheet_name}'에 새 행이 성공적으로 추가되었습니다.")
            return result
        except HttpError as error:
            logger.error(f"행 추가 API 오류: {error}")
            raise
        except Exception as e:
            logger.error(f"행 추가 중 오류 발생: {str(e)}")
            raise

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
                spreadsheetId=self.spreadsheet_id,
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
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            return result.get('values', [])
        except Exception as e:
            logger.error(f"Error reading range {range_name}: {e}")
            raise
    
    def append_values(self, range_name: str, values: List[List[Any]]) -> None:
        """Append values to the specified range"""
        try:
            logger.debug(f"Appending to range: {range_name}")
            body = {
                'values': values
            }
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            logger.debug("Append successful")
        except HttpError as e:
            logger.error(f"Error appending values: {e}", exc_info=True)
            raise

    def submit_answer(self, student_id, name, grade, problem_id, answer):
        """Submit a student's answer to the student_answers sheet"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Find the correct answer from problems sheet
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
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
            spreadsheetId=self.spreadsheet_id,
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

    def get_daily_problems(self, grade=None, count=20):
        """오늘 날짜에 해당하는 문제를 가져옵니다.
        
        Args:
            grade (str, optional): 학년 필터링 (중1, 중2, 중3 등)
            count (int, optional): 가져올 문제 수 (기본값: 20)
            
        Returns:
            list: 오늘의 문제 목록
        """
        try:
            # 모든 문제 가져오기
            all_problems = self.get_problems()
            
            if not all_problems:
                logger.warning("문제가 없습니다.")
                return []
            
            # 학년 형식 변환 함수
            def normalize_grade(grade_str):
                if not grade_str:
                    return ""
                
                # "중학교 1학년" -> "중1", "중학교 2학년" -> "중2" 등으로 변환
                if "중학교" in grade_str and "학년" in grade_str:
                    grade_num = ''.join(filter(str.isdigit, grade_str))
                    if grade_num:
                        return f"중{grade_num}"
                # "고등학교 1학년" -> "고1" 변환
                elif "고등학교" in grade_str and "학년" in grade_str:
                    grade_num = ''.join(filter(str.isdigit, grade_str))
                    if grade_num:
                        return f"고{grade_num}"
                return grade_str
            
            # 학년 필터링
            if grade:
                normalized_grade = grade
                filtered_problems = []
                
                for problem in all_problems:
                    problem_grade = problem.get('학년', '')
                    norm_problem_grade = normalize_grade(problem_grade)
                    
                    # 정규화된 학년 값이 일치하면 추가
                    if norm_problem_grade == normalized_grade:
                        filtered_problems.append(problem)
            else:
                filtered_problems = all_problems
            
            if not filtered_problems:
                logger.warning(f"{grade} 학년 문제가 없습니다.")
                return []
            
            # 날짜를 기준으로 랜덤 시드 설정 (매일 같은 결과가 나오도록)
            today = datetime.now().strftime('%Y-%m-%d')
            random.seed(f"{today}_{grade if grade else 'all'}")
            
            # 랜덤으로 문제 선택 (중복 없이)
            if len(filtered_problems) <= count:
                # 문제 수가 요청한 개수보다 적거나 같으면 모든 문제 반환
                daily_problems = filtered_problems
            else:
                # 충분한 문제가 있으면 랜덤으로 선택
                daily_problems = random.sample(filtered_problems, count)
            
            # 순서 섞기
            random.shuffle(daily_problems)
            
            logger.info(f"오늘({today})의 {grade if grade else '전체'} 문제 {len(daily_problems)}개를 가져왔습니다.")
            return daily_problems
            
        except Exception as e:
            logger.error(f"일일 문제 가져오기 중 오류 발생: {str(e)}")
            return []
    
    def get_weekly_problems(self, grade=None, problems_per_day=20, days=7):
        """주간 문제 계획을 생성합니다.
        
        Args:
            grade (str, optional): 학년 필터링
            problems_per_day (int, optional): 하루당 문제 수
            days (int, optional): 계획할 일수
            
        Returns:
            dict: 날짜별 문제 목록
        """
        try:
            weekly_problems = {}
            
            # 학년 형식 변환 함수
            def normalize_grade(grade_str):
                if not grade_str:
                    return ""
                
                # "중학교 1학년" -> "중1", "중학교 2학년" -> "중2" 등으로 변환
                if "중학교" in grade_str and "학년" in grade_str:
                    grade_num = ''.join(filter(str.isdigit, grade_str))
                    if grade_num:
                        return f"중{grade_num}"
                # "고등학교 1학년" -> "고1" 변환
                elif "고등학교" in grade_str and "학년" in grade_str:
                    grade_num = ''.join(filter(str.isdigit, grade_str))
                    if grade_num:
                        return f"고{grade_num}"
                return grade_str
            
            # 오늘부터 지정된 일수까지의 문제 생성
            for day in range(days):
                # 특정 날짜에 대한 시드 설정
                target_date = datetime.now() + timedelta(days=day)
                date_str = target_date.strftime('%Y-%m-%d')
                
                # 해당 날짜의 시드로 랜덤 시드 설정
                random.seed(f"{date_str}_{grade if grade else 'all'}")
                
                # 모든 문제 가져오기
                all_problems = self.get_problems()
                
                # 학년 필터링
                if grade:
                    normalized_grade = grade
                    filtered_problems = []
                    
                    for problem in all_problems:
                        problem_grade = problem.get('학년', '')
                        norm_problem_grade = normalize_grade(problem_grade)
                        
                        # 정규화된 학년 값이 일치하면 추가
                        if norm_problem_grade == normalized_grade:
                            filtered_problems.append(problem)
                else:
                    filtered_problems = all_problems
                
                # 해당 날짜의 문제 선택
                if len(filtered_problems) <= problems_per_day:
                    daily_problems = filtered_problems
                else:
                    daily_problems = random.sample(filtered_problems, problems_per_day)
                
                # 결과에 추가
                weekly_problems[date_str] = daily_problems
            
            logger.info(f"{days}일간의 문제 계획이 생성되었습니다.")
            return weekly_problems
            
        except Exception as e:
            logger.error(f"주간 문제 계획 생성 중 오류 발생: {str(e)}")
            return {} 