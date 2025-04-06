import subprocess
import sys
import os

def install_packages():
    """필요한 패키지를 설치합니다."""
    print("필요한 패키지를 설치합니다...")
    
    # 설치할 패키지 목록
    packages = [
        "streamlit",
        "pandas",
        "python-dotenv",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client"
    ]
    
    # pip 명령어 구성
    pip_command = [sys.executable, "-m", "pip", "install"]
    
    # 각 패키지 설치 시도
    for package in packages:
        try:
            print(f"{package} 설치 중...")
            subprocess.check_call(pip_command + [package])
            print(f"{package} 설치 완료!")
        except subprocess.CalledProcessError:
            print(f"{package} 설치 실패.")
    
    print("\n패키지 설치가 완료되었습니다.")
    print("이제 'python run_app.py' 명령으로 앱을 실행할 수 있습니다.")

if __name__ == "__main__":
    install_packages() 