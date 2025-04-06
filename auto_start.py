#!/usr/bin/env python
"""
학원 자동 첨삭 시스템 자동 시작 스크립트
- 다양한 시작 방법 시도
- 최적의 실행 방법 자동 선택
"""

import os
import sys
import subprocess
import time
import webbrowser

def print_header():
    """헤더를 출력합니다."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print(" " * 12 + "📚 학원 자동 첨삭 시스템 시작" + " " * 12)
    print("=" * 60)
    print("\n여러 방법으로 프로그램 시작을 시도합니다...\n")

def try_command(command, description, wait=3):
    """명령어 실행을 시도합니다."""
    print(f"시도 중: {description}")
    print(f"명령어: {command}")
    print("-" * 60)
    
    try:
        # 명령어 실행
        process = subprocess.Popen(command, shell=True)
        
        # 잠시 대기하여 오류 발생 여부 확인
        time.sleep(wait)
        
        # 프로세스가 여전히 실행 중인지 확인
        if process.poll() is None:
            print(f"✅ 성공! {description}가 실행 중입니다.")
            return True, process
        else:
            print(f"❌ 실패: {description}가 종료되었습니다.")
            return False, None
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False, None

def main():
    """메인 함수."""
    print_header()
    
    # Python 버전 확인
    print("Python 버전 확인 중...")
    try:
        python_version = subprocess.check_output(["py", "-V"]).decode().strip()
        print(f"Python 버전: {python_version}")
        print("py 명령어 사용 가능")
        py_command = "py"
    except:
        try:
            python_version = subprocess.check_output(["python", "-V"]).decode().strip()
            print(f"Python 버전: {python_version}")
            print("python 명령어 사용 가능")
            py_command = "python"
        except:
            print("❌ Python이 설치되어 있지 않거나 PATH에 등록되어 있지 않습니다.")
            input("계속하려면 엔터키를 누르세요...")
            return
    
    print("\n프로그램 시작 시도 중...\n")
    
    # 1. 콘솔 애플리케이션 실행 (no_dependency_app.py)
    success, process = try_command(f"{py_command} no_dependency_app.py", "콘솔 애플리케이션")
    if success:
        return
    
    # 2. 배치 파일 실행 시도
    if os.path.exists("start.bat"):
        success, process = try_command("start.bat", "배치 파일")
        if success:
            return
    
    # 3. py 명령어로 직접 실행
    success, process = try_command(f"py -E no_dependency_app.py", "Python 직접 실행 (가상환경 무시)")
    if success:
        return
    
    # 4. 브라우저에서 실행
    try:
        url = "http://localhost:8501"
        print(f"\n브라우저에서 애플리케이션 열기 시도: {url}")
        webbrowser.open(url)
        print("브라우저를 열었습니다. 애플리케이션이 이미 실행 중인지 확인하세요.")
    except:
        print("❌ 브라우저에서 열기 실패")
    
    print("\n모든 시도가 실패했습니다.")
    print("\n다음 방법을 수동으로 시도해보세요:")
    print("1. 명령 프롬프트에서 'py no_dependency_app.py' 실행")
    print("2. 'start.bat' 파일 더블클릭")
    
    input("\n계속하려면 엔터키를 누르세요...")

if __name__ == "__main__":
    main() 