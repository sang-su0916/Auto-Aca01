import os
import sys
import time
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def sync_google_sheets():
    """구글 스프레드시트 연결을 강제로 초기화하고 연동합니다."""
    print("\n===== 구글 스프레드시트 연동 절차 시작 =====")
    
    # 1. 환경 변수 재설정
    os.environ['GOOGLE_SHEETS_SPREADSHEET_ID'] = '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0'
    
    # 2. .env 파일 다시 작성
    with open(".env", "w", encoding="utf-8") as f:
        f.write("# Google Sheets API Configuration\n")
        f.write("GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0")
    print("✅ 환경 변수 파일(.env) 재설정 완료")
    
    # 3. 서비스 계정 파일 확인
    service_account_file = 'credentials.json'
    if not os.path.exists(service_account_file):
        print(f"❌ 오류: 서비스 계정 파일({service_account_file})이 존재하지 않습니다.")
        return False
    print("✅ 서비스 계정 파일(credentials.json) 확인 완료")
    
    # 4. Google Sheets API 초기화
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Google Sheets API 초기화 완료")
        
        # 5. 스프레드시트 정보 가져오기
        spreadsheet_id = '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0'
        print(f"연결 시도 중인 스프레드시트 ID: {spreadsheet_id}")
        
        try:
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheet_title = spreadsheet.get('properties', {}).get('title', '제목 없음')
            print(f"✅ 스프레드시트 연결 성공: '{sheet_title}'")
            
            # 6. 시트 목록 확인
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            print(f"현재 시트 목록: {', '.join(existing_sheets)}")
            
            # 7. 필요한 시트 생성
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
                print("✅ 필요한 시트 생성 완료")
                time.sleep(1)  # API 호출 사이에 약간의 딜레이
            else:
                print("✅ 모든 필요한 시트가 이미 존재합니다.")
            
            # 8. 헤더 설정
            problems_headers = [
                ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                 '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
            ]
            
            student_answers_headers = [
                ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
            ]
            
            # 9. 헤더 설정 (현재 데이터가 있더라도 덮어쓰기)
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
            print("✅ 헤더 설정 완료")
            
            # 10. 중복 문제 확인 및 제거 (간단한 문제 확인만 수행)
            try:
                problems_data = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range='problems!A2:N'
                ).execute()
                
                if 'values' in problems_data and problems_data['values']:
                    problems_count = len(problems_data['values'])
                    print(f"✅ problems 시트에 {problems_count}개의 문제가 있습니다.")
                else:
                    print("📋 problems 시트에 데이터가 없습니다. 추가 데이터 생성이 필요할 수 있습니다.")
            except Exception as e:
                print(f"문제 데이터 확인 중 오류: {str(e)}")
            
            print("\n===== 구글 스프레드시트 연동 완료 =====")
            print("✓ 앱에서 '문제 새로고침' 버튼을 클릭하여 문제를 로드하세요.")
            print("✓ 스프레드시트에 직접 접속하려면 다음 URL을 사용하세요:")
            print(f"  https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ 스프레드시트 연결 오류: {str(e)}")
            print("💡 다음 사항을 확인해주세요:")
            print("  1. 스프레드시트 ID가 올바른지 확인하세요.")
            print("  2. 서비스 계정에 스프레드시트 접근 권한이 있는지 확인하세요.")
            print(f"  3. 스프레드시트({spreadsheet_id})를 서비스 계정(credentials.json에 있는 이메일)과 공유했는지 확인하세요.")
            return False
            
    except Exception as e:
        print(f"❌ Google API 초기화 오류: {str(e)}")
        return False

if __name__ == "__main__":
    success = sync_google_sheets() 