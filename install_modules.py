import subprocess
import sys
import os

def install_package(package):
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print(f"{package} installed successfully!")

def main():
    print("===== 학원 자동 첨삭 시스템 모듈 설치 =====")
    print("필요한 Python 패키지를 설치합니다...")
    
    packages = [
        "streamlit",
        "pandas",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client"
    ]
    
    for package in packages:
        try:
            install_package(package)
        except Exception as e:
            print(f"Failed to install {package}: {str(e)}")
    
    print("\n설치 완료! 이제 'streamlit run app_without_sheets.py' 명령어로 앱을 실행할 수 있습니다.")
    print("Google Sheets API를 사용하려면 credentials.json 파일을 생성해야 합니다.")
    
    # 앱 시작
    user_input = input("\n지금 앱을 시작하시겠습니까? (y/n): ")
    if user_input.lower() == 'y':
        print("\n앱을 시작합니다...")
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_without_sheets.py"])
            print("앱이 시작되었습니다! 브라우저에서 http://localhost:8501 을 열어 확인하세요.")
        except Exception as e:
            print(f"앱 시작 중 오류가 발생했습니다: {str(e)}")
            print("다음 명령어를 직접 실행해보세요: python -m streamlit run app_without_sheets.py")

if __name__ == "__main__":
    main() 