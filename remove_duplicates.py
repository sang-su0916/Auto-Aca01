import os
import sys
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def remove_duplicate_problems():
    """스프레드시트에서 중복된 문제를 제거합니다."""
    print("\n===== 중복 문제 제거 시작 =====")
    
    # 1. 환경 변수 로드
    load_dotenv()
    
    # 2. 스프레드시트 ID 확인
    spreadsheet_id = '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0'
    print(f"스프레드시트 ID: {spreadsheet_id}")
    
    # 3. 서비스 계정 파일 확인
    service_account_file = 'credentials.json'
    if not os.path.exists(service_account_file):
        print(f"❌ 오류: 서비스 계정 파일({service_account_file})이 존재하지 않습니다.")
        return False
    
    try:
        # 4. Google Sheets API 초기화
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Google Sheets API 초기화 완료")
        
        # 5. 문제 데이터 가져오기
        problems_data = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='problems!A1:N'
        ).execute()
        
        if 'values' not in problems_data or len(problems_data['values']) <= 1:
            print("❌ problems 시트에 데이터가 없거나 헤더만 있습니다.")
            return False
        
        # 6. 헤더와 데이터 분리
        headers = problems_data['values'][0]
        rows = problems_data['values'][1:]
        
        # 7. 중복 확인을 위한 문제 ID 세트 생성
        problem_ids = set()
        unique_rows = []
        duplicates = []
        
        # 8. 중복 제거 (문제ID 기준)
        for row in rows:
            # 빈 행 또는 문제ID가 없는 행 건너뛰기
            if not row or len(row) == 0 or not row[0]:
                continue
                
            problem_id = row[0]
            if problem_id in problem_ids:
                duplicates.append(problem_id)
            else:
                problem_ids.add(problem_id)
                unique_rows.append(row)
        
        # 9. 결과 출력
        print(f"총 문제 수: {len(rows)}")
        print(f"고유 문제 수: {len(unique_rows)}")
        print(f"중복 문제 수: {len(duplicates)}")
        
        if len(duplicates) > 0:
            print(f"중복 문제 ID: {', '.join(duplicates[:5])}{'...' if len(duplicates) > 5 else ''}")
            
            # 10. 중복이 제거된 데이터로 시트 업데이트
            print("중복이 제거된 데이터로 시트 업데이트 중...")
            
            # 11. 먼저 시트 지우기 (헤더 제외)
            clear_request = service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range='problems!A2:N',
            ).execute()
            
            # 12. 고유한 데이터 다시 쓰기
            update_request = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='problems!A2',
                valueInputOption='RAW',
                body={'values': unique_rows}
            ).execute()
            
            print(f"✅ 중복 제거 완료: {len(duplicates)}개의 중복 문제가 제거되었습니다.")
        else:
            print("✅ 중복 문제가 없습니다.")
        
        # 13. 중복 문제 내용 확인 (문제 내용 기준)
        content_duplicates = []
        problem_contents = {}
        
        for i, row in enumerate(unique_rows):
            if len(row) > 5:  # 문제 내용이 있는지 확인
                content = row[5] if row[5] else ""
                if content in problem_contents:
                    content_duplicates.append((i, problem_contents[content]))
                else:
                    problem_contents[content] = i
        
        if content_duplicates:
            print(f"\n주의: 문제 내용이 동일한 {len(content_duplicates)}쌍의 문제가 있습니다.")
            print("문제 내용이 같지만 문제 ID가 다른 항목들입니다. 필요시 수동으로 확인하세요.")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    success = remove_duplicate_problems()
    if success:
        print("\n===== 작업 완료 =====")
        print("이제 앱에서 '문제 새로고침' 버튼을 클릭하여 문제를 다시 로드하세요.")
    else:
        print("\n❌ 작업 실패: 오류가 발생했습니다.") 