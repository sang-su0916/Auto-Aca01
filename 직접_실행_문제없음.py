import sys
import os
import time
import re
import pandas as pd
from datetime import datetime
import webbrowser
from threading import Timer

# 필요한 패키지 체크 및 설치
try:
    import streamlit
except ImportError:
    print("Streamlit이 설치되어 있지 않습니다. 설치합니다...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "pandas"])
    print("설치 완료!")
    import streamlit

# 상위 디렉토리 경로를 모듈 검색 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 자동 채점 함수
def grade_answer(problem_type, correct_answer, user_answer, keywords=None):
    if not user_answer:
        return 0, "답변을 입력하지 않았습니다."
    
    # 객관식 문제 채점
    if problem_type == '객관식':
        if user_answer.strip().lower() == correct_answer.strip().lower():
            return 100, "정답입니다!"
        else:
            return 0, f"오답입니다. 정답은 '{correct_answer}'입니다."
    
    # 주관식 문제 채점
    elif problem_type == '주관식':
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        
        # 정확히 일치하는 경우
        if user_answer == correct_answer:
            return 100, "정답입니다!"
        
        # 키워드 기반 부분 점수 채점
        if keywords:
            keyword_list = [k.strip().lower() for k in keywords.split(',')]
            matched_keywords = [k for k in keyword_list if k in user_answer]
            
            if matched_keywords:
                score = min(100, int(len(matched_keywords) / len(keyword_list) * 100))
                if score >= 80:
                    feedback = f"거의 정답입니다! 포함된 키워드: {', '.join(matched_keywords)}"
                elif score >= 50:
                    feedback = f"부분 정답입니다. 포함된 키워드: {', '.join(matched_keywords)}"
                else:
                    feedback = f"더 정확한 답변이 필요합니다. 정답은 '{correct_answer}'입니다."
                return score, feedback
        
        # 기본 피드백
        return 0, f"오답입니다. 정답은 '{correct_answer}'입니다."
    
    # 서술형 문제 채점
    elif problem_type == '서술형':
        user_answer = user_answer.strip().lower()
        
        # 키워드 기반 채점
        if keywords:
            keyword_list = [k.strip().lower() for k in keywords.split(',')]
            matched_keywords = [k for k in keyword_list if k in user_answer]
            
            score = min(100, int(len(matched_keywords) / len(keyword_list) * 100))
            
            if score >= 80:
                feedback = f"우수한 답변입니다! 포함된 키워드: {', '.join(matched_keywords)}"
            elif score >= 60:
                feedback = f"좋은 답변입니다. 포함된 키워드: {', '.join(matched_keywords)}"
            elif score >= 40:
                feedback = f"보통 수준의 답변입니다. 추가 키워드: {', '.join([k for k in keyword_list if k not in matched_keywords])}"
            else:
                feedback = f"더 자세한 답변이 필요합니다. 주요 키워드: {', '.join(keyword_list)}"
            
            return score, feedback
        
        # 기본 피드백
        return 50, "키워드 정보가 없어 정확한 채점이 어렵습니다. 교사의 확인이 필요합니다."
    
    return 0, "알 수 없는 문제 유형입니다."

# 샘플 문제 데이터 생성
def create_sample_data():
    # 샘플 문제 생성
    if not os.path.exists('sample_questions.csv'):
        problems = [
            {
                '문제ID': 'P001', '과목': '영어', '학년': '중3', '문제유형': '객관식', '난이도': '중',
                '문제내용': 'What is the capital of the UK?',
                '보기1': 'London', '보기2': 'Paris', '보기3': 'Berlin', '보기4': 'Rome', '보기5': '',
                '정답': 'London',
                '키워드': 'capital,UK,London',
                '해설': 'The capital city of the United Kingdom is London.'
            },
            {
                '문제ID': 'P002', '과목': '영어', '학년': '중3', '문제유형': '주관식', '난이도': '중',
                '문제내용': 'Write a sentence using the word "beautiful".',
                '보기1': '', '보기2': '', '보기3': '', '보기4': '', '보기5': '',
                '정답': 'The flower is beautiful.',
                '키워드': 'beautiful,sentence',
                '해설': '주어와 동사를 포함한 완전한 문장이어야 합니다.'
            },
            {
                '문제ID': 'P003', '과목': '영어', '학년': '중2', '문제유형': '객관식', '난이도': '하',
                '문제내용': 'Which word is a verb?',
                '보기1': 'happy', '보기2': 'book', '보기3': 'run', '보기4': 'fast', '보기5': '',
                '정답': 'run',
                '키워드': 'verb,part of speech',
                '해설': '동사(verb)는 행동이나 상태를 나타내는 품사입니다. run(달리다)은 동사입니다.'
            },
            {
                '문제ID': 'P004', '과목': '영어', '학년': '고1', '문제유형': '객관식', '난이도': '상',
                '문제내용': 'Choose the correct sentence.',
                '보기1': 'I have been to Paris last year.', '보기2': 'I went to Paris last year.',
                '보기3': 'I have went to Paris last year.', '보기4': 'I go to Paris last year.', '보기5': '',
                '정답': 'I went to Paris last year.',
                '키워드': 'grammar,past tense',
                '해설': '과거에 일어난 일에는 과거 시제(went)를 사용합니다.'
            },
            {
                '문제ID': 'P005', '과목': '영어', '학년': '고2', '문제유형': '주관식', '난이도': '중',
                '문제내용': 'What does "procrastination" mean?',
                '보기1': '', '보기2': '', '보기3': '', '보기4': '', '보기5': '',
                '정답': 'Delaying or postponing tasks',
                '키워드': 'vocabulary,meaning',
                '해설': 'Procrastination은 일이나 활동을 미루는 행동을 의미합니다.'
            }
        ]
        problems_df = pd.DataFrame(problems)
        problems_df.to_csv('sample_questions.csv', index=False, encoding='utf-8')
        print("샘플 문제가 생성되었습니다.")
    
    # 학생 답안 데이터 파일이 없으면 빈 파일 생성
    if not os.path.exists('student_answers.csv'):
        columns = ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
        pd.DataFrame(columns=columns).to_csv('student_answers.csv', index=False, encoding='utf-8')
        print("학생 답안 데이터 파일이 생성되었습니다.")

def main():
    print("학원 자동 첨삭 시스템을 시작합니다...")
    # 샘플 데이터 생성
    create_sample_data()
    
    # Streamlit 앱 실행
    try:
        print("웹 애플리케이션을 시작합니다...")
        app_path = os.path.join(current_dir, "app_without_sheets.py")
        
        # 스트림릿 서버 실행
        streamlit_cmd = [sys.executable, "-m", "streamlit", "run", app_path]
        
        # 브라우저 자동 실행 함수
        def open_browser():
            webbrowser.open('http://localhost:8501')
        
        # 3초 후 브라우저 열기
        Timer(3, open_browser).start()
        
        # 스트림릿 실행 (이 명령은 블로킹됨)
        print("잠시 후 브라우저가 자동으로 열립니다...")
        print("앱이 실행 중입니다. 종료하려면 Ctrl+C를 누르세요.")
        os.system(" ".join(streamlit_cmd))
        
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        print("다음 명령어를 직접 실행해보세요: streamlit run app_without_sheets.py")
        input("계속하려면 Enter 키를 누르세요...")

if __name__ == "__main__":
    main() 