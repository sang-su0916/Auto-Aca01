#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
구글 시트 초기화 스크립트
"""

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 구글 시트 ID
SPREADSHEET_ID = "1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def initialize_sheet():
    """시트 초기화 함수"""
    print(f"구글 시트 ID: {SPREADSHEET_ID}")
    
    # 인증 정보 파일 확인
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"오류: {CREDENTIALS_FILE} 파일을 찾을 수 없습니다.")
        return False
    
    try:
        # 인증 정보 생성
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        
        # 서비스 객체 생성
        service = build('sheets', 'v4', credentials=credentials)
        
        # 스프레드시트 정보 가져오기
        print("\n구글 시트 정보 조회 중...")
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID).execute()
        
        print(f"✅ 연결 성공! 스프레드시트 타이틀: '{spreadsheet['properties']['title']}'")
        
        # 시트 목록 확인
        sheets = spreadsheet.get('sheets', [])
        print("\n시트 목록:")
        sheet_titles = []
        for sheet in sheets:
            sheet_titles.append(sheet['properties']['title'])
            print(f"  - {sheet['properties']['title']}")
        
        # 필요한 시트 생성 또는 초기화
        required_sheets = ['problems', 'student_answers']
        
        for sheet_name in required_sheets:
            if sheet_name not in sheet_titles:
                # 새 시트 추가
                print(f"\n시트 '{sheet_name}'이 없습니다. 새로 생성합니다...")
                
                add_sheet_request = {
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }
                
                service.spreadsheets().batchUpdate(
                    spreadsheetId=SPREADSHEET_ID,
                    body={'requests': [add_sheet_request]}
                ).execute()
                
                print(f"✅ 시트 '{sheet_name}'이 생성되었습니다.")
            else:
                print(f"\n시트 '{sheet_name}'이 이미 존재합니다.")
        
        # 헤더 설정
        print("\n시트 헤더를 설정합니다...")
        
        # problems 시트 헤더
        problems_headers = [
            ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
             '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
        ]
        
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='problems!A1:N1',
            valueInputOption='RAW',
            body={'values': problems_headers}
        ).execute()
        
        print("✅ problems 시트 헤더가 설정되었습니다.")
        
        # student_answers 시트 헤더
        student_answers_headers = [
            ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
        ]
        
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='student_answers!A1:H1',
            valueInputOption='RAW',
            body={'values': student_answers_headers}
        ).execute()
        
        print("✅ student_answers 시트 헤더가 설정되었습니다.")
        
        # 샘플 문제 데이터 추가 여부 확인
        print("\n샘플 문제 데이터를 추가하시겠습니까? (y/n): ", end="")
        choice = input().lower()
        
        if choice == 'y':
            print("\n샘플 문제 데이터를 추가합니다...")
            
            # 샘플 데이터 추가
            sample_data = [
                ['P001', '영어', '중3', '객관식', '중', 'What is the capital of the UK?', 
                 'London', 'Paris', 'Berlin', 'Rome', '', '1', 'capital,UK,London', 
                 'The capital city of the United Kingdom is London.'],
                ['P002', '영어', '중3', '주관식', '중', 'Write a sentence using the word "beautiful".', 
                 '', '', '', '', '', 'The flower is beautiful.', 'beautiful,sentence', 
                 '주어와 동사를 포함한 완전한 문장이어야 합니다.'],
                ['P003', '영어', '중2', '객관식', '하', 'Which word is a verb?', 
                 'happy', 'book', 'run', 'fast', '', '3', 'verb,part of speech', 
                 '동사(verb)는 행동이나 상태를 나타내는 품사입니다. run(달리다)은 동사입니다.'],
                ['P004', '영어', '고1', '객관식', '상', 'Choose the correct sentence.', 
                 'I have been to Paris last year.', 'I went to Paris last year.', 'I have went to Paris last year.', 'I go to Paris last year.', '', 
                 '2', 'grammar,past tense', '과거에 일어난 일에는 과거 시제(went)를 사용합니다.'],
                ['P005', '영어', '고2', '주관식', '중', 'What does "procrastination" mean?', 
                 '', '', '', '', '', 'Delaying or postponing tasks', 'vocabulary,meaning', 
                 'Procrastination은 일이나 활동을 미루는 행동을 의미합니다.']
            ]
            
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range='problems!A2:N6',
                valueInputOption='RAW',
                body={'values': sample_data}
            ).execute()
            
            print(f"✅ {len(sample_data)}개의 샘플 문제가 추가되었습니다.")
        
        print("\n✅ 구글 시트 초기화가 완료되었습니다!")
        return True
    
    except HttpError as error:
        if error.resp.status == 404:
            print(f"❌ 오류: 스프레드시트를 찾을 수 없습니다. ID: {SPREADSHEET_ID}")
        elif error.resp.status == 403:
            print(f"❌ 오류: 스프레드시트 접근 권한이 없습니다. ID: {SPREADSHEET_ID}")
            print("\n권한 부여 방법:")
            print("1. 구글 스프레드시트에서 '공유' 버튼 클릭")
            print("2. 서비스 계정 이메일 입력")
            print("3. '편집자' 권한 선택 후 '완료' 클릭")
        else:
            print(f"❌ 구글 시트 API 오류: {error}")
        return False
    
    except Exception as e:
        print(f"❌ 초기화 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("===== 구글 시트 초기화 =====\n")
    initialize_sheet()
    print("\n작업이 완료되었습니다.") 