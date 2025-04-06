import os
import sys
import time
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json

def fix_sheets_connection():
    """구글 스프레드시트 연결의 모든 문제를 해결합니다."""
    print("\n==================================================")
    print("🔄 구글 스프레드시트 연결 문제 해결 도구")
    print("==================================================\n")
    
    # 1. Credentials 확인
    service_account_file = 'credentials.json'
    if not os.path.exists(service_account_file):
        print(f"❌ credentials.json 파일이 없습니다!")
        print("   서비스 계정 키 파일이 필요합니다.")
        return False
    
    # 2. 서비스 계정 정보 확인
    try:
        with open(service_account_file, 'r') as f:
            creds_data = json.load(f)
            service_email = creds_data.get('client_email', '알 수 없음')
        print(f"✅ 서비스 계정 이메일: {service_email}")
    except Exception as e:
        print(f"❌ credentials.json 파일을 읽을 수 없습니다: {str(e)}")
        return False
    
    # 3. 환경 변수 설정
    print("\n📝 환경 변수 설정 중...")
    spreadsheet_id = '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0'
    os.environ['GOOGLE_SHEETS_SPREADSHEET_ID'] = spreadsheet_id
    
    # 4. .env 파일 저장
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write("# Google Sheets API Configuration\n")
            f.write(f"GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}")
        print("✅ .env 파일에 설정 저장 완료")
    except Exception as e:
        print(f"⚠️ .env 파일 저장 중 오류: {str(e)}")
        print("   환경 변수는 메모리에 설정되었지만, 파일에는 저장되지 않았습니다.")
    
    # 5. API 초기화 및 연결 테스트
    print("\n🔄 Google Sheets API 연결 테스트 중...")
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)
        
        # 6. 스프레드시트 정보 확인
        print(f"📊 스프레드시트 ID로 연결 시도: {spreadsheet_id}")
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_title = spreadsheet.get('properties', {}).get('title', '알 수 없음')
        print(f"✅ 연결 성공! 스프레드시트 제목: {sheet_title}")
        
        # 7. 시트 확인 및 생성
        print("\n📋 시트 확인 중...")
        existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
        print(f"   현재 시트: {', '.join(existing_sheets)}")
        
        required_sheets = ['problems', 'student_answers']
        missing_sheets = [sheet for sheet in required_sheets if sheet not in existing_sheets]
        
        if missing_sheets:
            print(f"🔄 필요한 시트 생성 중: {', '.join(missing_sheets)}")
            requests = []
            for sheet_name in missing_sheets:
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                })
            
            body = {'requests': requests}
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            print("✅ 시트 생성 완료")
        else:
            print("✅ 모든 필요한 시트가 존재합니다")
        
        # 8. 헤더 설정
        print("\n📝 헤더 설정 중...")
        problems_headers = [
            ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
             '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
        ]
        
        student_answers_headers = [
            ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
        ]
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='problems!A1:N1',
            valueInputOption='RAW',
            body={'values': problems_headers}
        ).execute()
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='student_answers!A1:H1',
            valueInputOption='RAW',
            body={'values': student_answers_headers}
        ).execute()
        print("✅ 헤더 설정 완료")
        
        # 9. 중복 문제 확인 및 제거
        print("\n🔍 중복 문제 확인 중...")
        try:
            problems_data = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='problems!A2:N'
            ).execute()
            
            if 'values' in problems_data and problems_data['values']:
                rows = problems_data['values']
                print(f"   현재 {len(rows)}개의 문제가 있습니다")
                
                # 중복 확인
                problem_ids = set()
                unique_rows = []
                duplicates = []
                
                for row in rows:
                    if not row or len(row) == 0 or not row[0]:
                        continue
                    
                    problem_id = row[0]
                    if problem_id in problem_ids:
                        duplicates.append(problem_id)
                    else:
                        problem_ids.add(problem_id)
                        unique_rows.append(row)
                
                if duplicates:
                    print(f"⚠️ {len(duplicates)}개의 중복 문제 ID를 발견했습니다")
                    
                    # 중복 제거
                    print("🔄 중복 문제를 제거하는 중...")
                    
                    # 시트 클리어 후 고유 데이터만 다시 쓰기
                    clear_request = service.spreadsheets().values().clear(
                        spreadsheetId=spreadsheet_id,
                        range='problems!A2:N',
                    ).execute()
                    
                    update_request = service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range='problems!A2',
                        valueInputOption='RAW',
                        body={'values': unique_rows}
                    ).execute()
                    
                    print(f"✅ 중복 제거 완료: 이제 {len(unique_rows)}개의 고유한 문제만 남아있습니다")
                else:
                    print("✅ 중복 문제가 없습니다")
            else:
                print("⚠️ problems 시트에 문제 데이터가 없습니다")
        except Exception as e:
            print(f"⚠️ 중복 확인 중 오류: {str(e)}")
        
        # 10. 권한 공유 확인 및 추천
        print("\n💡 권한 확인")
        print(f"   이 스프레드시트({spreadsheet_id})에 다음 이메일을 편집자로 공유했는지 확인하세요:")
        print(f"   {service_email}")
        print("   스프레드시트 > 공유 > 사용자 추가 > 위 이메일 추가 > '편집자' 권한 부여")
        
        print("\n==================================================")
        print("✅ 모든 작업이 완료되었습니다!")
        print("==================================================")
        print("\n📋 연결 정보 요약:")
        print(f"   - 연결된 스프레드시트: {sheet_title}")
        print(f"   - 스프레드시트 ID: {spreadsheet_id}")
        print(f"   - 문제 수: {len(unique_rows) if 'unique_rows' in locals() else '알 수 없음'}")
        print("\n📝 다음 단계:")
        print("   1. Streamlit 앱 실행: py -m streamlit run app_simple.py")
        print("   2. 로그인 후 '문제 새로고침' 버튼을 눌러 최신 데이터 로드")
        print("   3. 변경사항 확인")
        print("\n🔗 스프레드시트 바로가기:")
        print(f"   https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        print("\n💡 문제 해결 방법:")
        print(f"   1. 스프레드시트({spreadsheet_id})가 존재하는지 확인하세요.")
        print(f"   2. 서비스 계정({service_email})에 스프레드시트 접근 권한이 있는지 확인하세요.")
        print("      스프레드시트 > 공유 > 사용자 추가 > 위 이메일 추가 > '편집자' 권한 부여")
        print("   3. credentials.json 파일이 올바르게 설정되어 있는지 확인하세요.")
        return False

if __name__ == "__main__":
    success = fix_sheets_connection() 