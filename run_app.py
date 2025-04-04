import subprocess
import sys
import os

def run_app():
    """
    pyvenv.cfg 파일 오류를 우회하여 Streamlit 앱을 실행합니다.
    Python 모듈 경로를 직접 지정하여 실행합니다.
    """
    print("학원 자동 첨삭 시스템을 시작합니다...")
    
    # 실행할 앱 파일 이름
    app_file = 'app_fixed.py'
    
    try:
        # Python 실행 경로
        python_executable = sys.executable
        
        # streamlit 모듈 직접 호출
        command = [
            python_executable, 
            "-m", 
            "streamlit.web.cli",
            "run",
            app_file
        ]
        
        print(f"실행 명령어: {' '.join(command)}")
        print("앱을 시작합니다. 브라우저가 자동으로 열릴 것입니다.")
        
        # 서브프로세스로 실행
        process = subprocess.Popen(command)
        
        print(f"앱이 실행 중입니다. 종료하려면 Ctrl+C를 누르세요.")
        process.wait()
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        print("Streamlit을 다시 설치해보세요: pip install streamlit")

if __name__ == "__main__":
    run_app() 