#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
구글 시트 연동 테스트 스크립트
이 스크립트는 구글 시트 API 연동이 제대로 작동하는지 테스트합니다.
"""

import os
import sys
import time
from dotenv import load_dotenv
from sheets.google_sheets import GoogleSheetsAPI

# .env 파일 로드
load_dotenv()

def main():
    """메인 테스트 함수"""
    print("===== 구글 시트 연동 테스트 =====")
    
    # API 클래스 초기화
    gs = GoogleSheetsAPI()
    
    # 연결 테스트
    print("\n[1] 연결 테스트")
    if not gs.is_connected():
        print("❌ Google Sheets API가 초기화되지 않았습니다.")
        print("setup_sheets_fresh.py를 실행하여 초기 설정을 완료하세요.")
        return False
    
    if not gs.test_connection():
        print("❌ 구글 시트 연결 테스트에 실패했습니다.")
        return False
    
    print("✅ 구글 시트에 성공적으로 연결되었습니다.")
    
    # 스프레드시트 ID 확인
    print(f"\n현재 사용 중인 스프레드시트 ID: {gs.spreadsheet_id}")
    
    # 문제 데이터 가져오기
    print("\n[2] 문제 데이터 가져오기")
    problems = gs.fetch_problems()
    if problems.empty:
        print("❌ 문제 데이터를 가져오는데 실패했습니다.")
        return False
    
    print(f"✅ 총 {len(problems)}개의 문제를 가져왔습니다.")
    
    # 첫 번째 문제 정보 출력
    if len(problems) > 0:
        first_problem = problems.iloc[0]
        print("\n첫 번째 문제 정보:")
        for key, value in first_problem.items():
            print(f"  - {key}: {value}")
    
    # 새 문제 추가 테스트
    print("\n[3] 새 문제 추가 테스트")
    new_problem_id = f"T{int(time.time())}"
    new_problem = {
        '문제ID': new_problem_id,
        '과목': '테스트',
        '학년': '테스트',
        '문제유형': '객관식',
        '난이도': '중',
        '문제내용': '이것은 테스트 문제입니다. 정답은?',
        '보기1': '테스트 보기 1',
        '보기2': '테스트 보기 2',
        '보기3': '테스트 보기 3',
        '보기4': '테스트 보기 4',
        '정답': '1',
        '해설': '테스트 문제 해설입니다.'
    }
    
    if not gs.add_problem(new_problem):
        print("❌ 새 문제 추가에 실패했습니다.")
        return False
    
    print(f"✅ 새 문제(ID: {new_problem_id})가 성공적으로 추가되었습니다.")
    
    # 잠시 대기
    print("업데이트 반영을 위해 2초 대기 중...")
    time.sleep(2)
    
    # 문제 업데이트 테스트
    print("\n[4] 문제 업데이트 테스트")
    update_data = {
        '문제내용': '이것은 업데이트된 테스트 문제입니다.',
        '난이도': '상'
    }
    
    if not gs.update_problem(new_problem_id, update_data):
        print("❌ 문제 업데이트에 실패했습니다.")
        return False
    
    print(f"✅ 문제(ID: {new_problem_id})가 성공적으로 업데이트되었습니다.")
    
    # 잠시 대기
    print("업데이트 반영을 위해 2초 대기 중...")
    time.sleep(2)
    
    # 업데이트된 문제 확인
    print("\n[5] 업데이트된 문제 확인")
    updated_problems = gs.fetch_problems()
    updated_problem = updated_problems[updated_problems['문제ID'] == new_problem_id]
    
    if updated_problem.empty:
        print("❌ 업데이트된 문제를 찾을 수 없습니다.")
        return False
    
    print("\n업데이트된 문제 정보:")
    for key, value in updated_problem.iloc[0].items():
        print(f"  - {key}: {value}")
    
    # 테스트 문제 삭제
    print("\n[6] 테스트 문제 삭제")
    if not gs.delete_problem(new_problem_id):
        print("❌ 테스트 문제 삭제에 실패했습니다.")
        return False
    
    print(f"✅ 테스트 문제(ID: {new_problem_id})가 성공적으로 삭제되었습니다.")
    
    print("\n===== 모든 테스트가 성공적으로 완료되었습니다 =====")
    print("구글 시트 연동이 정상적으로 작동 중입니다!")
    return True

if __name__ == "__main__":
    main() 