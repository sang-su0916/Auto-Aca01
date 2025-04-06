import os
import sys
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def setup_and_connect():
    # 환경변수 로드
    load_dotenv()
    
    # 스프레드시트 ID 설정 및 확인
    spreadsheet_id = '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0'
    os.environ['GOOGLE_SHEETS_SPREADSHEET_ID'] = spreadsheet_id
    
    print(f"구글 스프레드시트 ID 설정: {spreadsheet_id}")
    
    # 서비스 계정 파일 확인
    service_account_file = 'credentials.json'
    if not os.path.exists(service_account_file):
        print(f"오류: 서비스 계정 파일({service_account_file})이 존재하지 않습니다.")
        print("Google Cloud Console에서 서비스 계정을 만들고 키를 다운로드한 후 credentials.json으로 저장해주세요.")
        return False
    
    try:
        # Google Sheets API 초기화
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)
        
        # 스프레드시트 정보 가져오기 시도
        try:
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            print(f"연결된 스프레드시트: {spreadsheet.get('properties', {}).get('title', '제목 없음')}")
        except Exception as e:
            print(f"스프레드시트 접근 오류: {str(e)}")
            print("다음을 확인해주세요:")
            print("1. 제공된 스프레드시트 ID가 올바른지 확인")
            print("2. 서비스 계정 이메일에 스프레드시트 접근 권한을 부여했는지 확인")
            print("   - 스프레드시트 공유 버튼 클릭 > 서비스 계정 이메일 추가 > 편집자 권한 부여")
            return False
        
        # 필요한 시트 확인/생성
        existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
        print(f"현재 시트 목록: {', '.join(existing_sheets)}")
        
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
            service.spreadsheets().batchUpdate(
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
            
            # 샘플 문제 데이터 추가
            sample_problems = [
                [
                    'P001', '영어', '중3', '객관식', '중', 
                    'What is the capital of the UK?',
                    'London', 'Paris', 'Berlin', 'Rome', '', 
                    'London', 'capital,UK,London',
                    'The capital city of the United Kingdom is London.'
                ],
                [
                    'P002', '영어', '중3', '주관식', '중', 
                    'Write a sentence using the word "beautiful".',
                    '', '', '', '', '', 
                    'The flower is beautiful.', 'beautiful,sentence',
                    '주어와 동사를 포함한 완전한 문장이어야 합니다.'
                ]
            ]
            
            print("샘플 문제 추가 중...")
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='problems!A2',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': sample_problems}
            ).execute()
            print("샘플 문제 추가 완료")
        else:
            print("모든 필요한 시트가 이미 존재합니다.")

        # .env 파일 업데이트
        try:
            with open(".env", "w") as f:
                f.write("# Google Sheets API Configuration\n")
                f.write(f"GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}")
            print(".env 파일 업데이트 완료")
        except Exception as e:
            print(f".env 파일 업데이트 실패: {str(e)}")

        print("\n구글 스프레드시트 연결이 완료되었습니다!")
        print("앱에서 '문제 새로고침' 버튼을 클릭하여 문제를 로드하세요.")
        return True
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("구글 스프레드시트 연결 및 초기화 시작...")
    success = setup_and_connect()
    if success:
        print("구글 스프레드시트 연결 및 초기화 성공!")
        print("\n사용 방법:")
        print("1. 구글 시트에서 서비스 계정 이메일에 편집 권한을 부여해주세요.")
        print("2. 앱을 실행하고 '문제 새로고침' 버튼을 클릭하세요.")
        print("3. 문제와 학생 답변이 구글 시트와 동기화됩니다.")
    else:
        print("구글 스프레드시트 연결 실패!") 