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
            st.error("경고: Google API 인증 파일(credentials.json)을 찾을 수 없습니다. Google Sheets 연동이 작동하지 않을 수 있습니다.")
            print("GOOGLE_APPLICATION_CREDENTIALS_JSON 환경 변수가 설정되지 않았으며 로컬 credentials.json 파일도 없습니다.")
            
            # 개발 환경에서는 더미 credentials.json 생성 (테스트용)
            if not os.environ.get('STREAMLIT_SHARING'):
                try:
                    # 최소한의 더미 credentials 생성
                    dummy_creds = {
                        "type": "service_account",
                        "project_id": "dummy-project",
                        "private_key_id": "dummy",
                        "private_key": "-----BEGIN PRIVATE KEY-----\ndummy\n-----END PRIVATE KEY-----\n",
                        "client_email": "dummy@example.com",
                        "client_id": "123456789",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy%40example.com"
                    }
                    with open('credentials.json', 'w') as f:
                        json.dump(dummy_creds, f)
                    print("개발 환경용 더미 credentials.json 파일이 생성되었습니다.")
                    return True
                except Exception as e:
                    print(f"더미 credentials 생성 중 오류 발생: {str(e)}")
                    return False
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
    
    if not spreadsheet_id:
        st.error("Google Sheets 스프레드시트 ID가 설정되지 않았습니다. 환경 변수 GOOGLE_SHEETS_SPREADSHEET_ID를 설정해주세요.")
        # 기본값 설정 (필요한 경우 여기서 하드코딩할 수 있음)
        spreadsheet_id = "11a93BT5FR_hr61nxulETCM0xuxy2BuBNnxU6mTz2XzU"
        print(f"기본 스프레드시트 ID가 사용됩니다: {spreadsheet_id}")
    
    return spreadsheet_id

# Streamlit Cloud에서 실행 시 자동 설정
if __name__ == "__main__":
    setup_credentials()
    spreadsheet_id = get_spreadsheet_id()
    
    if spreadsheet_id:
        print(f"스프레드시트 ID: {spreadsheet_id}")
    else:
        print("스프레드시트 ID를 찾을 수 없습니다.") 