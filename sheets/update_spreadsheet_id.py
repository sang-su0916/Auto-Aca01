import os
import sys
from dotenv import load_dotenv

def update_spreadsheet_id():
    # 환경변수 로드
    load_dotenv()
    
    # 새 스프레드시트 ID 설정
    new_spreadsheet_id = '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0'
    
    print(f"새 구글 스프레드시트 ID: {new_spreadsheet_id}")
    
    # .env 파일 업데이트
    try:
        with open(".env", "w") as f:
            f.write("# Google Sheets API Configuration\n")
            f.write(f"GOOGLE_SHEETS_SPREADSHEET_ID={new_spreadsheet_id}")
        print(".env 파일이 성공적으로 업데이트되었습니다.")
    except Exception as e:
        print(f".env 파일 업데이트 실패: {str(e)}")
        return False
    
    # 필요한 경우 sheets/setup_sheets.py 파일도 업데이트
    try:
        # setup_sheets.py 파일 읽기
        with open("sheets/setup_sheets.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # SPREADSHEET_ID 변수 찾아서 대체
        import re
        updated_content = re.sub(
            r"SPREADSHEET_ID\s*=\s*'[^']*'",
            f"SPREADSHEET_ID = '{new_spreadsheet_id}'",
            content
        )
        
        # 업데이트된 내용 쓰기
        with open("sheets/setup_sheets.py", "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print("setup_sheets.py 파일도 업데이트되었습니다.")
    except Exception as e:
        print(f"setup_sheets.py 업데이트 실패: {str(e)}")
    
    # google_sheets.py 파일에서 기본값으로 사용되는 ID도 업데이트
    try:
        # google_sheets.py 파일 읽기
        with open("sheets/google_sheets.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 기본 ID 변수 찾아서 대체
        import re
        updated_content = re.sub(
            r'self\.SPREADSHEET_ID = "[^"]*"',
            f'self.SPREADSHEET_ID = "{new_spreadsheet_id}"',
            content
        )
        
        # 업데이트된 내용 쓰기
        with open("sheets/google_sheets.py", "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print("google_sheets.py 파일도 업데이트되었습니다.")
    except Exception as e:
        print(f"google_sheets.py 업데이트 실패: {str(e)}")
    
    print("\n스프레드시트 ID가 성공적으로 업데이트되었습니다!")
    print("이제 앱에서 구글 시트와 연결할 수 있습니다.")
    return True

if __name__ == "__main__":
    print("구글 스프레드시트 ID 업데이트 시작...")
    success = update_spreadsheet_id()
    if success:
        print("구글 스프레드시트 ID 업데이트 성공!")
    else:
        print("구글 스프레드시트 ID 업데이트 실패!") 