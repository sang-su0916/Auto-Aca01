import os
import sys
import warnings

# 필요한 패키지 확인 함수
def check_packages():
    required_packages = [
        "python-dotenv",
        "google-auth",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "google-api-python-client",
        "streamlit",
        "pandas"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} 설치됨")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} 설치되지 않음")
    
    return missing_packages

# 환경 설정 확인 함수
def check_environment():
    # 가상환경 확인
    is_venv = sys.prefix != sys.base_prefix
    print(f"\n가상환경 사용 여부: {'✓ 사용 중' if is_venv else '✗ 사용하지 않음'}")
    
    # .env 파일 확인
    has_env = os.path.exists('.env')
    print(f".env 파일: {'✓ 존재함' if has_env else '✗ 존재하지 않음'}")
    
    # credentials.json 확인
    has_credentials = os.path.exists('credentials.json')
    print(f"credentials.json 파일: {'✓ 존재함' if has_credentials else '✗ 존재하지 않음'}")
    
    # sheets 디렉토리 확인
    has_sheets_dir = os.path.exists('sheets') and os.path.isdir('sheets')
    print(f"sheets 디렉토리: {'✓ 존재함' if has_sheets_dir else '✗ 존재하지 않음'}")
    
    # __init__.py 확인
    has_init = os.path.exists('sheets/__init__.py')
    print(f"sheets/__init__.py 파일: {'✓ 존재함' if has_init else '✗ 존재하지 않음'}")
    
    return is_venv, has_env, has_credentials, has_sheets_dir, has_init

# 구글 시트 연동 확인 함수
def check_google_sheets_connection():
    print("\n구글 시트 연동 확인 중...")
    
    try:
        # .env 파일 로드
        from dotenv import load_dotenv
        load_dotenv()
        
        # 환경 변수 확인
        sheets_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
        if not sheets_id:
            print("✗ GOOGLE_SHEETS_SPREADSHEET_ID 환경 변수가 설정되지 않았습니다.")
            return False
        print(f"✓ GOOGLE_SHEETS_SPREADSHEET_ID 환경 변수: {sheets_id}")
        
        # 인증 확인
        from google.oauth2 import service_account
        try:
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            print("✓ credentials.json 파일로 인증 성공")
            
            # API 연결 확인
            from googleapiclient.discovery import build
            service = build('sheets', 'v4', credentials=credentials)
            sheet = service.spreadsheets()
            
            # 스프레드시트 정보 가져오기 시도
            result = sheet.get(spreadsheetId=sheets_id).execute()
            print(f"✓ 구글 시트 '{result['properties']['title']}' 연결 성공")
            return True
            
        except Exception as e:
            print(f"✗ 구글 시트 연동 실패: {str(e)}")
            return False
    
    except Exception as e:
        print(f"✗ 구글 시트 연동 확인 중 오류 발생: {str(e)}")
        return False

def main():
    print("가상환경 및 구글 시트 연동 설정 확인을 시작합니다...")
    
    # 패키지 확인
    print("\n1. 필요한 패키지 확인:")
    missing_packages = check_packages()
    
    # 환경 확인
    print("\n2. 환경 설정 확인:")
    is_venv, has_env, has_credentials, has_sheets_dir, has_init = check_environment()
    
    # 구글 시트 연동 확인
    sheets_connected = False
    if has_credentials and has_env:
        sheets_connected = check_google_sheets_connection()
    else:
        print("\n구글 시트 연동을 확인하기 위해 .env 파일과 credentials.json 파일이 필요합니다.")
    
    # 요약 및 조치 사항
    print("\n======= 설정 확인 요약 =======")
    if not missing_packages and is_venv and has_env and has_credentials and has_sheets_dir and has_init and sheets_connected:
        print("✓ 모든 설정이 완료되었습니다! 앱을 실행할 준비가 되었습니다.")
    else:
        print("다음 조치가 필요합니다:")
        
        if missing_packages:
            packages_str = " ".join(missing_packages)
            print(f"- 다음 패키지를 설치하세요: pip install {packages_str}")
            
        if not is_venv:
            print("- 가상환경을 생성하고 활성화하세요: py -m venv sheets_venv && call sheets_venv\\Scripts\\activate.bat")
            
        if not has_env:
            print("- .env 파일을 생성하세요.")
            
        if not has_credentials:
            print("- Google API 콘솔에서 서비스 계정 키를 다운로드하여 credentials.json으로 저장하세요.")
            
        if not has_sheets_dir or not has_init:
            print("- sheets 디렉토리와 __init__.py 파일을 생성하세요.")
            
        if not sheets_connected and has_credentials and has_env:
            print("- 구글 시트 연동 설정을 확인하세요.")

if __name__ == "__main__":
    # 경고 무시
    warnings.filterwarnings("ignore")
    main() 