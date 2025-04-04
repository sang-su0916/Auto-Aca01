#!/usr/bin/env python
"""
학원 자동 첨삭 시스템 시작 스크립트
- 가상환경 의존성 우회
- 외부 모듈 의존성 없음
"""

import os
import sys
import subprocess

def clear_screen():
    """화면을 지웁니다."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """헤더를 출력합니다."""
    clear_screen()
    print("=" * 60)
    print(" " * 12 + "📚 학원 자동 첨삭 시스템" + " " * 12)
    print("=" * 60)
    print("\n애플리케이션을 시작합니다...\n")

def main():
    """메인 함수."""
    print_header()
    
    # Python 실행 파일 경로
    python_exe = sys.executable
    
    # 실행할 파일 경로
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "no_dependency_app.py")
    
    print(f"Python: {python_exe}")
    print(f"애플리케이션: {app_path}")
    print("\n애플리케이션을 시작합니다...")
    print("=" * 60)
    
    try:
        # -E 옵션: 환경 변수와 가상환경 무시
        cmd = [python_exe, "-E", app_path]
        
        # 서브프로세스로 실행 (현재 프로세스 대체)
        if os.name == 'nt':  # Windows
            subprocess.call(cmd)
        else:  # Linux/Mac
            os.execv(python_exe, cmd)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        print("\n다른 방법을 시도합니다...")
        
        try:
            # 일반 실행 시도
            if os.name == 'nt':  # Windows
                subprocess.call([python_exe, app_path])
            else:  # Linux/Mac
                os.execv(python_exe, [python_exe, app_path])
        except Exception as e2:
            print(f"\n두 번째 시도 실패: {e2}")
            print("\n시스템 Python으로 직접 실행을 시도합니다...")
            
            try:
                # 시스템 Python으로 직접 실행
                os.system(f"python {app_path}")
            except Exception as e3:
                print(f"\n모든 시도 실패: {e3}")
                input("\n계속하려면 엔터키를 누르세요...")

if __name__ == "__main__":
    main() 