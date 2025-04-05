import os
import sys
import time
import json
import traceback
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def fix_google_sheets_connection():
    """구글 스프레드시트 연결 문제를 강제로 해결합니다"""
    print("\n==================================================")
    print("🛠️  구글 스프레드시트 연동 문제 해결 도구 v2.0")
    print("==================================================\n")
    
    # 1. 환경 설정
    spreadsheet_id = '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0'
    service_account_file = 'credentials.json'
    
    # 2. 서비스 계정 확인
    if not os.path.exists(service_account_file):
        print(f"❌ 오류: credentials.json 파일이 없습니다!")
        print("   해결 방법: 서비스 계정 키 파일을 현재 폴더에 다운로드하세요.")
        return False
    
    # 3. 서비스 계정 정보 읽기
    try:
        with open(service_account_file, 'r') as f:
            creds_data = json.load(f)
            service_email = creds_data.get('client_email', '알 수 없음')
        print(f"✅ 서비스 계정 확인: {service_email}")
    except Exception as e:
        print(f"❌ 오류: credentials.json 파일을 읽을 수 없습니다: {str(e)}")
        print("   해결 방법: 올바른 형식의 서비스 계정 키 파일을 다운로드하세요.")
        return False
    
    # 4. 환경 변수 강제 설정
    print(f"📝 스프레드시트 ID 설정: {spreadsheet_id}")
    os.environ['GOOGLE_SHEETS_SPREADSHEET_ID'] = spreadsheet_id
    
    # 5. .env 파일 강제 재작성
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write("# Google Sheets API Configuration\n")
            f.write(f"GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}")
        print("✅ .env 파일 업데이트 완료")
    except Exception as e:
        print(f"⚠️ .env 파일 저장 중 오류: {str(e)}")
    
    # 6. API 연결 시도
    print("\n🔄 Google Sheets API 연결 시도 중...")
    try:
        # 스코프 설정
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        
        # 인증 정보 생성
        credentials = Credentials.from_service_account_file(
            service_account_file, scopes=scopes)
        
        # 서비스 객체 생성
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ API 클라이언트 초기화 성공")
        
        # 7. 스프레드시트 연결 테스트
        try:
            spreadsheet = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id).execute()
            
            sheet_title = spreadsheet.get('properties', {}).get('title', '제목 없음')
            print(f"✅ 스프레드시트 연결 성공: '{sheet_title}'")
            
            # 8. 시트 확인 및 생성
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            print(f"\n📋 현재 시트: {', '.join(existing_sheets)}")
            
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
                
                # 새로 시트를 만든 경우 1초 대기
                time.sleep(1)
            else:
                print("✅ 필요한 모든 시트 존재 확인")
            
            # 9. 헤더 설정
            print("\n📝 헤더 설정 중...")
            problems_headers = [
                ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                 '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
            ]
            
            student_answers_headers = [
                ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
            ]
            
            # 문제 헤더 설정
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='problems!A1:N1',
                valueInputOption='RAW',
                body={'values': problems_headers}
            ).execute()
            
            # 답안 헤더 설정
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='student_answers!A1:H1',
                valueInputOption='RAW',
                body={'values': student_answers_headers}
            ).execute()
            
            print("✅ 헤더 설정 완료")
            
            # 10. 중복 문제 확인 및 제거
            print("\n🔍 중복 문제 검사 중...")
            try:
                # 모든 문제 데이터 가져오기
                problems_data = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range='problems!A2:N'
                ).execute()
                
                if 'values' in problems_data and problems_data['values']:
                    rows = problems_data['values']
                    initial_count = len(rows)
                    print(f"   총 {initial_count}개의 문제 발견")
                    
                    # 중복 제거
                    problem_ids = {}  # ID -> 행 인덱스
                    unique_rows = []
                    duplicates = []
                    
                    for i, row in enumerate(rows):
                        # 빈 행 또는 ID가 없는 행 건너뛰기
                        if not row or len(row) == 0 or not row[0]:
                            continue
                        
                        problem_id = row[0].strip()
                        if problem_id in problem_ids:
                            duplicates.append(problem_id)
                        else:
                            problem_ids[problem_id] = i
                            unique_rows.append(row)
                    
                    # 중복이 있으면 제거
                    if duplicates:
                        print(f"⚠️ {len(duplicates)}개의 중복 문제 ID 발견")
                        print(f"   중복 문제 ID: {', '.join(duplicates[:5])}" + 
                              ("..." if len(duplicates) > 5 else ""))
                        
                        # 시트 클리어
                        print("🔄 중복 문제 제거 중...")
                        clear_request = service.spreadsheets().values().clear(
                            spreadsheetId=spreadsheet_id,
                            range='problems!A2:N'
                        ).execute()
                        
                        # 고유 데이터만 쓰기
                        update_request = service.spreadsheets().values().update(
                            spreadsheetId=spreadsheet_id,
                            range='problems!A2',
                            valueInputOption='RAW',
                            body={'values': unique_rows}
                        ).execute()
                        
                        print(f"✅ 중복 제거 완료: {len(duplicates)}개 제거됨")
                        print(f"   원래 {initial_count}개 → 현재 {len(unique_rows)}개")
                    else:
                        print("✅ 중복 문제가 없습니다")
                        
                    # 11. 데이터 확인
                    print("\n📊 문제 데이터 요약:")
                    print(f"   총 문제 수: {len(unique_rows)}")
                    
                    # 학년별 문제 수 계산
                    grades = {}
                    for row in unique_rows:
                        if len(row) > 2:  # 학년 정보가 있는지 확인
                            grade = row[2] if row[2] else "미분류"
                            grades[grade] = grades.get(grade, 0) + 1
                    
                    if grades:
                        print("   학년별 문제 수:")
                        for grade, count in sorted(grades.items()):
                            print(f"     - {grade}: {count}개")
                else:
                    print("⚠️ problems 시트에 데이터가 없습니다")
                    print("   문제를 직접 추가하거나 샘플 데이터를 생성해야 합니다")
            except Exception as e:
                print(f"⚠️ 중복 확인 중 오류: {str(e)}")
                traceback.print_exc()
            
            # 12. 권한 공유 확인
            print("\n📢 권한 확인 필요!")
            print(f"   스프레드시트({spreadsheet_id})에 다음 이메일이 '편집자'로 공유되어 있어야 합니다:")
            print(f"   {service_email}")
            print(f"   ✓ 공유 방법: 스프레드시트 우상단 '공유' → '{service_email}' 추가 → '편집자' 권한 설정")
            
            # 13. 성공 메시지 및 요약
            print("\n==================================================")
            print("✅ 구글 스프레드시트 연동 설정 완료!")
            print("==================================================")
            print(f"\n📋 연결 정보:")
            print(f"   스프레드시트: {sheet_title}")
            print(f"   스프레드시트 ID: {spreadsheet_id}")
            print(f"   서비스 계정: {service_email}")
            print(f"   문제 수: {len(unique_rows) if 'unique_rows' in locals() else '알 수 없음'}")
            
            # 14. 다음 단계 안내
            print("\n📝 다음 단계:")
            print("   1. Streamlit 앱 실행: py -m streamlit run app_simple.py")
            print("   2. 로그인 후 '교사' 계정으로 접속하여 '문제 새로고침' 버튼 클릭")
            print("   3. 문제가 제대로 로드되는지 확인")
            
            return True
            
        except HttpError as e:
            status_code = e.resp.status
            reason = e.resp.reason
            
            print(f"❌ API 오류: {status_code} {reason}")
            
            if status_code == 404:
                print("💡 문제 원인: 스프레드시트를 찾을 수 없습니다.")
                print(f"   해결 방법: '{spreadsheet_id}' ID가 올바른지 확인하세요.")
            elif status_code == 403:
                print("💡 문제 원인: 권한이 없습니다.")
                print(f"   해결 방법: 스프레드시트를 '{service_email}'과 공유했는지 확인하세요.")
                print("             '공유' 버튼 → 이메일 추가 → '편집자' 권한 설정")
            
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        print(f"💡 자세한 오류 정보:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔄 구글 스프레드시트 연결 문제 해결 도구 실행 중...")
    result = fix_google_sheets_connection()
    
    if result:
        print("\n🎉 성공! 이제 앱을 실행하세요: py -m streamlit run app_simple.py")
    else:
        print("\n❌ 문제가 해결되지 않았습니다. 위의 오류 메시지를 확인하세요.") 