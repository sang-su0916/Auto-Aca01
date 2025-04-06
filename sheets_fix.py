"""
구글 시트 연동 문제 해결 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

def create_env_file():
    """환경 변수 파일 생성"""
    env_path = Path('.env')
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("GOOGLE_SHEETS_SPREADSHEET_ID=1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0\n")
        print("✅ .env 파일 생성 완료")
        return True
    except Exception as e:
        print(f"❌ .env 파일 생성 실패: {str(e)}")
        return False

def create_sheets_dir():
    """sheets 디렉토리 생성"""
    sheets_dir = Path('sheets')
    try:
        if not sheets_dir.exists():
            sheets_dir.mkdir()
        
        # __init__.py 파일 생성
        init_file = sheets_dir / "__init__.py"
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write("# Initialize the sheets package\n")
        
        print("✅ sheets 디렉토리 설정 완료")
        return True
    except Exception as e:
        print(f"❌ sheets 디렉토리 설정 실패: {str(e)}")
        return False

def install_packages():
    """필요한 패키지 설치"""
    packages = [
        "python-dotenv",
        "google-auth",
        "google-auth-oauthlib", 
        "google-auth-httplib2",
        "google-api-python-client",
        "pandas",
        "streamlit"
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--no-warn-script-location", package])
            print(f"✅ {package} 설치 완료")
        except Exception as e:
            print(f"❌ {package} 설치 실패: {str(e)}")
    
    return True

def main():
    """메인 함수"""
    print("===== 구글 시트 연동 문제 해결 =====")
    
    # 환경 변수 파일 생성
    create_env_file()
    
    # sheets 디렉토리 생성
    create_sheets_dir()
    
    # 패키지 설치
    install_packages()
    
    print("\n===== 설정 완료 =====")
    print("이제 다음 명령어로 앱을 실행하세요:")
    print("streamlit run app.py")

if __name__ == "__main__":
    main() 