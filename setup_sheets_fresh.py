#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# .env 파일 로드
load_dotenv()

# 상수 정의
CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def get_spreadsheet_id():
    """환경 변수에서 스프레드시트 ID 가져오기"""
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    if not spreadsheet_id:
        print("경고: 환경 변수에 GOOGLE_SHEETS_SPREADSHEET_ID가 설정되지 않았습니다.")
        print("새 스프레드시트를 생성합니다...")
        return None
    return spreadsheet_id

def create_service():
    """Google Sheets API 서비스 객체 생성"""
    try:
        # 인증 정보 파일 확인
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"오류: {CREDENTIALS_FILE} 파일을 찾을 수 없습니다.")
            print("Google Cloud Console에서 서비스 계정 키(JSON)를 다운로드하여 프로젝트 루트에 저장하세요.")
            return None

        # 인증 정보 생성
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        
        # 서비스 객체 생성
        service = build('sheets', 'v4', credentials=credentials)
        print("Google Sheets API 서비스가 성공적으로 초기화되었습니다.")
        return service
    except Exception as e:
        print(f"Google Sheets API 초기화 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def create_new_spreadsheet(service):
    """새 스프레드시트 생성"""
    spreadsheet_body = {
        'properties': {
            'title': '학원 자동 첨삭 시스템 - 문제 데이터'
        },
        'sheets': [
            {
                'properties': {
                    'title': '테스트 데이터',
                }
            }
        ]
    }
    
    try:
        request = service.spreadsheets().create(body=spreadsheet_body)
        response = request.execute()
        
        spreadsheet_id = response['spreadsheetId']
        print(f"새 스프레드시트가 생성되었습니다. ID: {spreadsheet_id}")
        
        # .env 파일에 스프레드시트 ID 저장
        with open('.env', 'r', encoding='utf-8') as file:
            content = file.read()
        
        if 'GOOGLE_SHEETS_SPREADSHEET_ID' in content:
            # 기존 ID 업데이트
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('GOOGLE_SHEETS_SPREADSHEET_ID='):
                    lines[i] = f'GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}'
                    break
            
            new_content = '\n'.join(lines)
        else:
            # 새 ID 추가
            new_content = content
            if not content.endswith('\n'):
                new_content += '\n'
            new_content += f'GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}\n'
        
        with open('.env', 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(".env 파일에 스프레드시트 ID가 저장되었습니다.")
        
        return spreadsheet_id
    except Exception as e:
        print(f"스프레드시트 생성 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def initialize_spreadsheet(service, spreadsheet_id):
    """스프레드시트 초기화 및 헤더/샘플 데이터 설정"""
    try:
        # 헤더 설정
        headers = [
            ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
             '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
        ]
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='테스트 데이터!A1:N1',
            valueInputOption='RAW',
            body={'values': headers}
        ).execute()
        
        print("스프레드시트 헤더가 설정되었습니다.")
        
        # 샘플 데이터 추가
        sample_data = []
        subjects = ["영어", "수학", "국어", "과학", "사회"]
        grades = ["중1", "중2", "중3", "고1", "고2", "고3"]
        difficulties = ["상", "중", "하"]
        problem_types = ["객관식", "주관식"]
        
        for i in range(1, 11):
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
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='테스트 데이터!A2:N',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': sample_data}
        ).execute()
        
        print(f"스프레드시트에 {len(sample_data)}개의 샘플 문제가 추가되었습니다.")
        
        return True
    except Exception as e:
        print(f"스프레드시트 초기화 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_connection(service, spreadsheet_id):
    """구글 시트 연결 테스트"""
    try:
        # 스프레드시트 정보 가져오기
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id).execute()
        
        print(f"✅ 구글 시트 연결 테스트 성공! 타이틀: '{spreadsheet['properties']['title']}'")
        
        # 시트 목록 확인
        sheets = spreadsheet.get('sheets', [])
        print("시트 목록:")
        for sheet in sheets:
            print(f"  - {sheet['properties']['title']}")
        
        return True
    except HttpError as error:
        if error.resp.status == 404:
            print(f"❌ 오류: 스프레드시트를 찾을 수 없습니다. ID: {spreadsheet_id}")
            print("스프레드시트 ID가 올바른지 확인하거나, 새 스프레드시트를 생성하세요.")
        elif error.resp.status == 403:
            print(f"❌ 오류: 스프레드시트 접근 권한이 없습니다. ID: {spreadsheet_id}")
            print("서비스 계정 이메일에 스프레드시트 편집 권한을 부여했는지 확인하세요.")
            credentials = Credentials.from_service_account_file(CREDENTIALS_FILE)
            print(f"서비스 계정 이메일: {credentials.service_account_email}")
        else:
            print(f"❌ 구글 시트 API 오류: {error}")
        return False
    except Exception as e:
        print(f"❌ 연결 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def share_spreadsheet(service, spreadsheet_id):
    """스프레드시트 공유 설정"""
    try:
        # Drive API 서비스 생성
        drive_service = build('drive', 'v3', credentials=service._credentials)
        
        # 서비스 계정 이메일 가져오기
        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE)
        service_account_email = credentials.service_account_email
        
        # 공유 설정
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body={
                'type': 'user',
                'role': 'writer',
                'emailAddress': service_account_email
            }
        ).execute()
        
        print(f"스프레드시트가 서비스 계정({service_account_email})과 공유되었습니다.")
        print("이제 앱에서 스프레드시트에 접근할 수 있습니다.")
        
        return True
    except Exception as e:
        print(f"스프레드시트 공유 설정 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 실행 함수"""
    print("===== 구글 시트 연동 설정 =====")
    
    # 서비스 객체 생성
    service = create_service()
    if not service:
        print("Google Sheets API 서비스를 초기화할 수 없습니다.")
        return False
    
    # 스프레드시트 ID 가져오기
    spreadsheet_id = get_spreadsheet_id()
    
    # 기존 스프레드시트 테스트
    if spreadsheet_id:
        print(f"기존 스프레드시트 ID: {spreadsheet_id}")
        if test_connection(service, spreadsheet_id):
            print("기존 스프레드시트에 성공적으로 연결되었습니다.")
            
            # 사용자 입력 받기
            while True:
                choice = input("기존 스프레드시트를 사용하시겠습니까? (y/n): ").lower()
                if choice in ('y', 'yes', 'n', 'no'):
                    break
                print("'y' 또는 'n'으로 응답해주세요.")
            
            if choice in ('y', 'yes'):
                print("기존 스프레드시트를 사용합니다.")
                return True
    
    # 새 스프레드시트 생성
    print("새 스프레드시트를 생성합니다...")
    new_spreadsheet_id = create_new_spreadsheet(service)
    if not new_spreadsheet_id:
        print("새 스프레드시트를 생성할 수 없습니다.")
        return False
    
    # 스프레드시트 공유 설정
    if not share_spreadsheet(service, new_spreadsheet_id):
        print("스프레드시트 공유 설정에 실패했습니다.")
    
    # 스프레드시트 초기화
    if not initialize_spreadsheet(service, new_spreadsheet_id):
        print("스프레드시트 초기화에 실패했습니다.")
        return False
    
    print("\n===== 구글 시트 연동 완료 =====")
    print(f"스프레드시트 ID: {new_spreadsheet_id}")
    print("이제 앱에서 구글 시트 데이터를 사용할 수 있습니다.")
    return True

if __name__ == "__main__":
    main() 