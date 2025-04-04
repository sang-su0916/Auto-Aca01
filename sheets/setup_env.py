import os
import json
import streamlit as st
from typing import Optional

def setup_credentials():
    """Streamlit Cloud 환경 변수에서 credentials.json 설정을 처리합니다"""
    creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    
    if creds_json:
        try:
            # JSON 문자열을 파싱하여 올바른 형식인지 확인
            creds_dict = json.loads(creds_json)
            
            # 임시 credentials.json 파일 생성
            with open('credentials.json', 'w') as f:
                json.dump(creds_dict, f)
                
            print("Credentials.json 파일이 환경 변수에서 성공적으로 생성되었습니다.")
            return True
        except Exception as e:
            print(f"Credentials 생성 중 오류 발생: {str(e)}")
            return False
    else:
        # 로컬 credentials.json 파일 확인
        if os.path.exists('credentials.json'):
            print("로컬 credentials.json 파일이 존재합니다.")
            return True
        else:
            print("GOOGLE_APPLICATION_CREDENTIALS_JSON 환경 변수가 설정되지 않았으며 로컬 credentials.json 파일도 없습니다.")
            return False

def get_spreadsheet_id() -> Optional[str]:
    """환경 변수 또는 .env 파일에서 스프레드시트 ID를 가져옵니다"""
    # 환경 변수에서 먼저 확인
    spreadsheet_id = os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID')
    
    if not spreadsheet_id:
        # .env 파일에서 확인 (dotenv가 이미 로드되었다고 가정)
        from dotenv import load_dotenv
        load_dotenv()
        spreadsheet_id = os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID')
    
    return spreadsheet_id

# Streamlit Cloud에서 실행 시 자동 설정
if __name__ == "__main__":
    setup_credentials()
    spreadsheet_id = get_spreadsheet_id()
    
    if spreadsheet_id:
        print(f"스프레드시트 ID: {spreadsheet_id}")
    else:
        print("스프레드시트 ID를 찾을 수 없습니다.") 