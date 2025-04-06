import os
import sys
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def reset_sheets_connection():
    """구글 스프레드시트 연결을 초기화하고 확인합니다."""
    print("구글 스프레드시트 연결 초기화 시작...")
    
    # 환경변수 로드
    load_dotenv()
    
    # 스프레드시트 ID 확인
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    if not spreadsheet_id:
        spreadsheet_id = "1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0"
        os.environ['GOOGLE_SHEETS_SPREADSHEET_ID'] = spreadsheet_id
    
    print(f"사용 중인 스프레드시트 ID: {spreadsheet_id}")
    
    # 서비스 계정 파일 확인
    service_account_file = 'credentials.json'
    if not os.path.exists(service_account_file):
        print(f"오류: 서비스 계정 파일({service_account_file})이 존재하지 않습니다.")
        return False
    
    try:
        # Google Sheets API 초기화
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)
        
        # 스프레드시트 정보 가져오기
        print(f"스프레드시트({spreadsheet_id}) 정보 가져오기 시도 중...")
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        sheet_title = spreadsheet.get('properties', {}).get('title', '제목 없음')
        print(f"스프레드시트 제목: {sheet_title}")
        
        # 시트 목록 확인
        existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
        print(f"현재 시트 목록: {', '.join(existing_sheets)}")
        
        # problems, student_answers 시트가 있는지 확인
        required_sheets = ['problems', 'student_answers']
        missing_sheets = [sheet for sheet in required_sheets if sheet not in existing_sheets]
        
        if missing_sheets:
            print(f"경고: 다음 필수 시트가 없습니다: {', '.join(missing_sheets)}")
            print("'initialize_sheets.py' 스크립트를 실행하여 필요한 시트를 생성해주세요.")
        else:
            print("✅ 모든 필수 시트가 존재합니다.")
            
            # 헤더 확인
            try:
                problems_headers = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range='problems!A1:N1'
                ).execute()
                
                if 'values' in problems_headers and problems_headers['values']:
                    print("✅ problems 시트 헤더가 설정되어 있습니다.")
                else:
                    print("경고: problems 시트에 헤더가 설정되어 있지 않습니다.")
                
                # 데이터 존재 여부 확인
                problems_data = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range='problems!A2:N'
                ).execute()
                
                if 'values' in problems_data and problems_data['values']:
                    print(f"✅ problems 시트에 {len(problems_data['values'])}개의 문제가 있습니다.")
                else:
                    print("경고: problems 시트에 데이터가 없습니다.")
                
                print("\n구글 스프레드시트 연결이 정상적으로 설정되었습니다.")
                print("앱에서 '문제 새로고침' 버튼을 클릭하여 문제를 로드하세요.")
                return True
            
            except Exception as e:
                print(f"시트 내용 확인 중 오류 발생: {str(e)}")
                return False
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    reset_sheets_connection() 