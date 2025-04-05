import os
import sys
from sheets.setup_sheets import GoogleSheetsSetup
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sheets():
    """스프레드시트에 필요한 시트를 생성하고 초기화합니다."""
    try:
        # 환경 변수 확인
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        if not spreadsheet_id:
            spreadsheet_id = "1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0"
            os.environ['GOOGLE_SHEETS_SPREADSHEET_ID'] = spreadsheet_id
            print(f"스프레드시트 ID 설정: {spreadsheet_id}")
        
        # 서비스 계정 파일 확인
        service_account_file = 'credentials.json'
        if not os.path.exists(service_account_file):
            logger.error(f"서비스 계정 파일({service_account_file})이 존재하지 않습니다.")
            return False
        
        # Google Sheets API 초기화
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)
        
        # 스프레드시트 정보 가져오기
        print(f"스프레드시트({spreadsheet_id}) 정보 가져오기 시도 중...")
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        print(f"스프레드시트 제목: {spreadsheet.get('properties', {}).get('title', '제목 없음')}")
        
        # 필요한 시트 확인/생성
        existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
        print(f"기존 시트: {', '.join(existing_sheets)}")
        
        required_sheets = ['problems', 'student_answers']
        requests = []
        
        for sheet_name in required_sheets:
            if sheet_name not in existing_sheets:
                print(f"'{sheet_name}' 시트 생성 필요")
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                })
        
        if requests:
            print("시트 생성 중...")
            body = {'requests': requests}
            result = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            print("시트 생성 완료")
            
            # 헤더 설정
            problems_headers = [
                ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                 '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
            ]
            
            student_answers_headers = [
                ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
            ]
            
            print("problems 시트 헤더 설정 중...")
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='problems!A1:N1',
                valueInputOption='RAW',
                body={'values': problems_headers}
            ).execute()
            
            print("student_answers 시트 헤더 설정 중...")
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='student_answers!A1:H1',
                valueInputOption='RAW',
                body={'values': student_answers_headers}
            ).execute()
            
            print("헤더 설정 완료")
        else:
            print("모든 필요한 시트가 이미 존재합니다.")
        
        # GoogleSheetsSetup 클래스를 사용하여 샘플 문제 추가
        print("GoogleSheetsSetup을 사용하여 시트 초기화 시도 중...")
        setup = GoogleSheetsSetup()
        if setup.service:
            setup.initialize_sheets()
            print("시트 초기화 및 샘플 문제 추가 완료")
        else:
            print("GoogleSheetsSetup 초기화 실패")
        
        return True
    
    except Exception as e:
        logger.error(f"오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("구글 스프레드시트 초기화 시작...")
    success = create_sheets()
    if success:
        print("구글 스프레드시트 초기화 성공!")
    else:
        print("구글 스프레드시트 초기화 실패!") 