#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON 파일을 앱에 업로드하는 스크립트
"""

import os
import json
import shutil
import sys
from datetime import datetime

# 앱 데이터 파일 경로
APP_DATA_DIR = "data"
PROBLEMS_FILE = os.path.join(APP_DATA_DIR, "problems.json")
BACKUP_DIR = os.path.join(APP_DATA_DIR, "backups")

def ensure_dirs_exist():
    """필요한 디렉토리가 존재하는지 확인하고, 없으면 생성"""
    if not os.path.exists(APP_DATA_DIR):
        os.makedirs(APP_DATA_DIR)
        print(f"'{APP_DATA_DIR}' 디렉토리를 생성했습니다.")
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"'{BACKUP_DIR}' 디렉토리를 생성했습니다.")

def backup_existing_file():
    """기존 파일 백업"""
    if os.path.exists(PROBLEMS_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"problems_{timestamp}.json"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        shutil.copy2(PROBLEMS_FILE, backup_path)
        print(f"기존 파일을 '{backup_path}'로 백업했습니다.")
        return True
    return False

def load_json_file(json_file_path):
    """JSON 파일 로드"""
    try:
        if not os.path.exists(json_file_path):
            print(f"오류: '{json_file_path}' 파일을 찾을 수 없습니다.")
            return None
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"'{json_file_path}' 파일에서 데이터를 성공적으로 로드했습니다.")
        if isinstance(data, list):
            print(f"총 {len(data)}개의 문제가 포함되어 있습니다.")
        return data
    except json.JSONDecodeError:
        print(f"오류: '{json_file_path}'가 올바른 JSON 형식이 아닙니다.")
        return None
    except Exception as e:
        print(f"파일 로드 중 오류 발생: {str(e)}")
        return None

def save_to_app(data):
    """데이터를 앱에 저장"""
    try:
        with open(PROBLEMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"데이터를 앱의 '{PROBLEMS_FILE}' 파일에 성공적으로 저장했습니다.")
        return True
    except Exception as e:
        print(f"앱에 데이터 저장 중 오류 발생: {str(e)}")
        return False

def main():
    print("JSON 파일을 앱에 업로드하는 스크립트를 시작합니다...")
    
    # 명령줄 인수 처리
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
    else:
        json_file_path = "problems.json"  # 기본 파일명
    
    # 필요한 디렉토리 확인 및 생성
    ensure_dirs_exist()
    
    # 기존 파일 백업
    backup_existing_file()
    
    # JSON 파일 로드
    data = load_json_file(json_file_path)
    if data is None:
        return
    
    # 앱에 데이터 저장
    if save_to_app(data):
        print("\n업로드 완료! 앱이 이제 새 문제 데이터를 사용할 수 있습니다.")
    else:
        print("\n업로드 실패!")

if __name__ == "__main__":
    main() 