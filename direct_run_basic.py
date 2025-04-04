import sys
import os

# 현재 디렉토리 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("📚 학원 자동 첨삭 시스템 (기본 버전)을 시작합니다...")
print("이 버전은 Google Sheets API를 사용하지 않습니다.")
print("데이터는 메모리에만 저장되며, 앱을 종료하면 초기화됩니다.")

try:
    # 필요한 패키지 확인 및 설치
    required_packages = ["pandas", "streamlit"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} 패키지가 이미 설치되어 있습니다.")
        except ImportError:
            print(f"✗ {package} 패키지가 설치되어 있지 않습니다. 설치를 시도합니다...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} 설치 완료!")

    # 실행 명령어
    run_command = f"{sys.executable} -m streamlit.cli run app_basic.py"
    print("\n다음 명령어로 앱을 실행합니다:")
    print("-----------------------------------------------")
    print(run_command)
    print("-----------------------------------------------")
    
    # 자동 실행
    print("\n앱을 시작합니다. 잠시만 기다려주세요...")
    os.system(run_command)

except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    print("다음 명령어를 터미널에 직접 입력해보세요:")
    print(f"python -m streamlit run app_basic.py")
    
    input("\n계속하려면 엔터 키를 누르세요...") 