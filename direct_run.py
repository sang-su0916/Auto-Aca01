import sys
import os

# 필요한 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("학원 자동 첨삭 시스템을 시작합니다...")

try:
    # 필요한 패키지 확인 및 설치
    required_packages = ["pandas", "streamlit"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} 패키지가 설치되어 있지 않습니다. 설치를 시도합니다...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} 설치 완료!")

    # 직접 실행 명령어 안내
    print("\n다음 명령어로 앱을 실행하세요:")
    print("-----------------------------------------------")
    print(f"{sys.executable} -m streamlit.web.cli run app_fixed.py")
    print("-----------------------------------------------")
    
    # 사용자 편의를 위해 자동 복사
    try:
        import pyperclip
        pyperclip.copy(f"{sys.executable} -m streamlit.web.cli run app_fixed.py")
        print("명령어가 클립보드에 복사되었습니다. Ctrl+V로 붙여넣기 할 수 있습니다.")
    except:
        pass  # pyperclip이 설치되지 않은 경우 무시
    
    # 실행 여부 확인
    response = input("\n지금 앱을 실행할까요? (y/n): ")
    if response.lower() == 'y':
        os.system(f'"{sys.executable}" -m streamlit.web.cli run app_fixed.py')
    else:
        print("위 명령어를 복사하여 직접 실행할 수 있습니다.")

except Exception as e:
    print(f"오류 발생: {str(e)}")
    print("수동으로 다음 명령을 실행해보세요:")
    print(f"{sys.executable} -m streamlit.web.cli run app_fixed.py") 