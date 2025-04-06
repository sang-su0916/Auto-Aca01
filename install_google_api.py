import os
import sys
import subprocess
import site
import importlib

def install_packages():
    """필요한 패키지를 설치합니다."""
    packages = [
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "python-dotenv",
        "streamlit"
    ]
    
    print(f"파이썬 버전: {sys.version}")
    print(f"설치 경로: {sys.prefix}")
    
    try:
        for package in packages:
            print(f"{package} 설치 중...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("모든 패키지가 성공적으로 설치되었습니다.")
    except Exception as e:
        print(f"패키지 설치 중 오류 발생: {e}")
        
        # 사용자 디렉토리에 설치 시도
        try:
            print("사용자 디렉토리에 설치 시도 중...")
            for package in packages:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
            print("사용자 디렉토리에 모든 패키지가 성공적으로 설치되었습니다.")
        except Exception as e:
            print(f"사용자 디렉토리 설치 중 오류 발생: {e}")
            
            # 현재 디렉토리에 설치 시도
            try:
                print("현재 디렉토리에 설치 시도 중...")
                for package in packages:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target=.", package])
                print("현재 디렉토리에 모든 패키지가 성공적으로 설치되었습니다.")
            except Exception as e:
                print(f"현재 디렉토리 설치 중 오류 발생: {e}")

def test_imports():
    """Google API 패키지 임포트를 테스트합니다."""
    modules_to_test = [
        "google.oauth2",
        "googleapiclient",
        "dotenv",
        "streamlit"
    ]
    
    print("\n모듈 임포트 테스트:")
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"✓ {module_name} 성공적으로 임포트됨")
        except ImportError as e:
            print(f"✗ {module_name} 임포트 실패: {e}")

def setup_path():
    """Python 모듈 검색 경로를 설정합니다."""
    # 현재 디렉토리 추가
    current_dir = os.path.abspath(os.path.dirname(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # site-packages 디렉토리 출력
    print("\nPython 패키지 경로:")
    for path in site.getsitepackages():
        print(f"- {path}")
    
    # 사용자 site-packages 경로 추가
    user_site = site.getusersitepackages()
    print(f"사용자 패키지 경로: {user_site}")
    if user_site not in sys.path:
        sys.path.append(user_site)

def main():
    """메인 함수"""
    print("Google API 설치 스크립트를 시작합니다...\n")
    
    setup_path()
    install_packages()
    test_imports()
    
    print("\n설치 스크립트 완료!")
    print("이제 다음 명령으로 앱을 실행해 보세요:")
    print("streamlit run app.py")

if __name__ == "__main__":
    main() 