import os
import sys
import subprocess
import webbrowser
import time

def check_python_installed():
    """Python이 설치되어 있는지 확인합니다."""
    try:
        subprocess.run(["python", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        try:
            subprocess.run(["py", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False

def create_csv_files():
    """필요한 CSV 파일이 없으면 생성합니다."""
    # app_without_google.py가 실행되면 파일을 자동으로 생성하므로 이 부분은 실제로 필요하지 않습니다
    pass

def run_app():
    """앱을 실행합니다."""
    print("학원 자동 첨삭 시스템을 시작합니다...")
    
    if not check_python_installed():
        print("Python이 설치되어 있지 않습니다.")
        print("https://www.python.org/downloads/ 에서 Python을 설치한 후 다시 실행해주세요.")
        input("계속하려면 아무 키나 누르세요...")
        return False
    
    # 필요한 패키지 설치
    print("필요한 패키지를 확인합니다...")
    subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "pandas"], 
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 애플리케이션 실행
    print("학원 자동 첨삭 시스템을 실행합니다...")
    
    # 먼저 app_without_google.py가 있는지 확인
    if os.path.exists("app_without_google.py"):
        app_file = "app_without_google.py"
    else:
        print("app_without_google.py 파일을 찾을 수 없습니다.")
        return False
    
    # 브라우저 창 열기
    time.sleep(2)  # 서버가 시작될 시간을 주기 위해 잠시 대기
    webbrowser.open('http://localhost:8501')
    
    # Streamlit 앱 실행
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", app_file])
    
    return True

if __name__ == "__main__":
    success = run_app()
    
    if not success:
        print("애플리케이션을 시작하는 중 오류가 발생했습니다.")
        print("수동으로 다음 명령을 실행해보세요:")
        print("python -m streamlit run app_without_google.py")
        
    input("종료하려면 아무 키나 누르세요...") 