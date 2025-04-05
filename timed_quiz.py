import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import random

# Google Sheets API 연결
def connect_to_sheets():
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'credentials.json'
        
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        
        # 환경 변수에서 스프레드시트 ID 가져오기
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        if not spreadsheet_id:
            # 기본값 사용
            spreadsheet_id = "1YcKaHcjnx5-WypEpYbcfg04s8TIq280l-gi6iISF5NQ"
        
        return service, spreadsheet_id
    except Exception as e:
        st.error(f"Google Sheets 연결 오류: {str(e)}")
        return None, None

# 문제 데이터 가져오기
def get_problems(service, spreadsheet_id):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='problems!A2:N'
        ).execute()
        
        values = result.get('values', [])
        problems = []
        
        for row in values:
            # 모든 열이 존재하도록 확장
            row_extended = row + [''] * (14 - len(row)) if len(row) < 14 else row
            
            problem = {
                '문제ID': row_extended[0],
                '과목': row_extended[1],
                '학년': row_extended[2],
                '문제유형': row_extended[3],
                '난이도': row_extended[4],
                '문제내용': row_extended[5],
                '보기1': row_extended[6],
                '보기2': row_extended[7],
                '보기3': row_extended[8],
                '보기4': row_extended[9],
                '보기5': row_extended[10],
                '정답': row_extended[11],
                '키워드': row_extended[12],
                '해설': row_extended[13]
            }
            problems.append(problem)
        
        return problems
    except Exception as e:
        st.error(f"문제 로드 오류: {str(e)}")
        return []

# 학생 답변 가져오기
def get_student_answers(service, spreadsheet_id, student_id):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='student_answers!A2:H'
        ).execute()
        
        values = result.get('values', [])
        answers = []
        
        for row in values:
            if len(row) > 0 and row[0] == student_id:
                # 모든 열이 존재하도록 확장
                row_extended = row + [''] * (8 - len(row)) if len(row) < 8 else row
                
                answer = {
                    '학생ID': row_extended[0],
                    '이름': row_extended[1],
                    '학년': row_extended[2],
                    '문제ID': row_extended[3],
                    '제출답안': row_extended[4],
                    '점수': float(row_extended[5]) if row_extended[5] else 0,
                    '피드백': row_extended[6],
                    '제출시간': row_extended[7]
                }
                answers.append(answer)
        
        return answers
    except Exception as e:
        st.error(f"학생 답변 로드 오류: {str(e)}")
        return []

# 답변 저장하기
def save_answer(service, spreadsheet_id, answer_data):
    try:
        values = [[
            answer_data['학생ID'],
            answer_data['이름'],
            answer_data['학년'], 
            answer_data['문제ID'],
            answer_data['제출답안'],
            answer_data['점수'],
            answer_data['피드백'],
            answer_data['제출시간']
        ]]
        
        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='student_answers!A:H',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return True
    except Exception as e:
        st.error(f"답변 저장 오류: {str(e)}")
        return False

# 자동 채점 기능
def grade_answer(problem_type, correct_answer, user_answer, keywords=None):
    if not user_answer:
        return 0, "답변을 입력하지 않았습니다."
    
    # 객관식 문제 채점
    if problem_type == '객관식':
        if user_answer.strip() == correct_answer.strip():
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
                    feedback = f"더 정확한 답변이 필요합니다."
                return score, feedback
        
        # 기본 피드백
        return 0, f"오답입니다. 정답은 '{correct_answer}'입니다."
    
    return 0, "알 수 없는 문제 유형입니다."

# 학생별 취약 유형 분석
def analyze_weak_points(answers, problems):
    if not answers:
        return {}
    
    # 문제 ID로 문제 조회를 위한 딕셔너리
    problem_dict = {p['문제ID']: p for p in problems}
    
    # 유형별 성적 집계 (키워드, 문제유형, 학년)
    keyword_scores = {}
    type_scores = {}
    
    for answer in answers:
        problem_id = answer['문제ID']
        score = answer['점수']
        
        if problem_id in problem_dict:
            problem = problem_dict[problem_id]
            
            # 키워드별 성적 집계
            if problem['키워드']:
                for keyword in problem['키워드'].split(','):
                    keyword = keyword.strip()
                    if keyword not in keyword_scores:
                        keyword_scores[keyword] = []
                    keyword_scores[keyword].append(score)
            
            # 문제유형별 성적 집계
            problem_type = problem['문제유형']
            if problem_type not in type_scores:
                type_scores[problem_type] = []
            type_scores[problem_type].append(score)
    
    # 평균 점수 계산
    keyword_avg = {}
    for keyword, scores in keyword_scores.items():
        keyword_avg[keyword] = sum(scores) / len(scores) if scores else 0
    
    type_avg = {}
    for problem_type, scores in type_scores.items():
        type_avg[problem_type] = sum(scores) / len(scores) if scores else 0
    
    # 취약 키워드 및 유형 (60점 미만인 경우)
    weak_keywords = [k for k, v in keyword_avg.items() if v < 60]
    weak_types = [t for t, v in type_avg.items() if v < 60]
    
    return {
        'keyword_avg': keyword_avg,
        'type_avg': type_avg,
        'weak_keywords': weak_keywords,
        'weak_types': weak_types
    }

# 학생별 맞춤 문제 선택
def select_custom_problems(problems, student_analysis, student_grade, count=20):
    if not problems:
        return []
    
    # 학년에 맞는 문제만 필터링
    grade_problems = [p for p in problems if p['학년'] == student_grade]
    
    if not grade_problems:
        return []
    
    selected_problems = []
    
    # 취약 키워드/유형이 있는 경우 우선 선택
    weak_keyword_problems = []
    if 'weak_keywords' in student_analysis and student_analysis['weak_keywords']:
        for problem in grade_problems:
            if problem['키워드']:
                problem_keywords = [k.strip() for k in problem['키워드'].split(',')]
                if any(wk in problem_keywords for wk in student_analysis['weak_keywords']):
                    weak_keyword_problems.append(problem)
    
    weak_type_problems = []
    if 'weak_types' in student_analysis and student_analysis['weak_types']:
        for problem in grade_problems:
            if problem['문제유형'] in student_analysis['weak_types']:
                weak_type_problems.append(problem)
    
    # 취약 문제를 우선 선택 (최대 60%)
    weak_problems = list(set(weak_keyword_problems + weak_type_problems))
    random.shuffle(weak_problems)
    
    weak_count = min(int(count * 0.6), len(weak_problems))
    selected_problems.extend(weak_problems[:weak_count])
    
    # 나머지는 랜덤 선택
    remaining_problems = [p for p in grade_problems if p not in selected_problems]
    random.shuffle(remaining_problems)
    
    remaining_count = count - len(selected_problems)
    selected_problems.extend(remaining_problems[:remaining_count])
    
    # 최종적으로 문제를 섞음
    random.shuffle(selected_problems)
    
    return selected_problems[:count]

# 타이머 표시 함수
def display_timer(start_time, time_limit_minutes):
    elapsed_time = datetime.now() - start_time
    remaining_time = timedelta(minutes=time_limit_minutes) - elapsed_time
    
    if remaining_time.total_seconds() <= 0:
        st.error("시간이 종료되었습니다!")
        return True  # 시간 종료
    
    minutes, seconds = divmod(int(remaining_time.total_seconds()), 60)
    st.sidebar.markdown(f"""
    <div style='text-align: center; background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>
        <h2 style='margin: 0;'>남은 시간</h2>
        <h1 style='margin: 0; color: {'green' if minutes > 5 else 'orange' if minutes > 1 else 'red'};'>
            {minutes:02d}:{seconds:02d}
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    return False  # 시간 남음

# 메인 함수
def run_timed_quiz():
    st.title("학원 자동 첨삭 시스템 - 시간제한 테스트")
    
    # Google Sheets API 연결
    service, spreadsheet_id = connect_to_sheets()
    
    if not service or not spreadsheet_id:
        st.error("Google Sheets 연결에 실패했습니다. 로컬 모드로 실행합니다.")
        return
    
    # 세션 상태 초기화
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'custom_problems' not in st.session_state:
        st.session_state.custom_problems = []
    if 'current_problem_index' not in st.session_state:
        st.session_state.current_problem_index = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'time_limit_minutes' not in st.session_state:
        st.session_state.time_limit_minutes = 30  # 기본 30분
    if 'time_expired' not in st.session_state:
        st.session_state.time_expired = False
    
    # 사용자 정보 가져오기 (세션에서)
    user_data = st.session_state.get('user_data')
    
    if not user_data or user_data['role'] != 'student':
        st.warning("학생 계정으로 로그인해야 이용할 수 있습니다.")
        return
    
    student_id = user_data['username']
    student_name = user_data['name']
    student_grade = user_data['grade']
    
    if not st.session_state.quiz_started and not st.session_state.quiz_completed:
        st.subheader("맞춤형 시간제한 테스트")
        st.write(f"{student_name} 학생의 취약 유형 분석 결과에 맞춰 문제가 출제됩니다.")
        
        # 문제 및 학생 답변 가져오기
        problems = get_problems(service, spreadsheet_id)
        student_answers = get_student_answers(service, spreadsheet_id, student_id)
        
        # 취약 유형 분석
        analysis = analyze_weak_points(student_answers, problems)
        
        if analysis.get('weak_keywords'):
            st.write("**취약한 키워드:**", ", ".join(analysis['weak_keywords']))
        
        if analysis.get('weak_types'):
            st.write("**취약한 문제 유형:**", ", ".join(analysis['weak_types']))
        
        col1, col2 = st.columns(2)
        with col1:
            time_limit = st.selectbox("시간 제한", [15, 20, 30, 40, 60], index=2)
        with col2:
            problem_count = st.selectbox("문제 수", [10, 15, 20, 25, 30], index=2)
        
        if st.button("테스트 시작"):
            # 맞춤형 문제 선택
            custom_problems = select_custom_problems(problems, analysis, student_grade, problem_count)
            
            if not custom_problems:
                st.error(f"{student_grade} 학년에 맞는 문제가 없습니다.")
                return
            
            st.session_state.quiz_started = True
            st.session_state.custom_problems = custom_problems
            st.session_state.current_problem_index = 0
            st.session_state.answers = {}
            st.session_state.start_time = datetime.now()
            st.session_state.time_limit_minutes = time_limit
            st.session_state.time_expired = False
            
            st.rerun()
    
    elif st.session_state.quiz_started and not st.session_state.quiz_completed:
        # 타이머 표시
        time_expired = display_timer(st.session_state.start_time, st.session_state.time_limit_minutes)
        if time_expired and not st.session_state.time_expired:
            st.session_state.time_expired = True
            st.rerun()
        
        # 진행 상황 표시
        total_problems = len(st.session_state.custom_problems)
        current_index = st.session_state.current_problem_index
        progress = (current_index + 1) / total_problems
        
        st.progress(progress)
        st.write(f"문제 {current_index + 1} / {total_problems}")
        
        # 현재 문제 표시
        current_problem = st.session_state.custom_problems[current_index]
        
        st.subheader(f"[{current_problem['난이도']}] {current_problem['문제내용']}")
        
        # 문제 유형에 따라 다른 입력 위젯 표시
        answer_key = f"answer_{current_problem['문제ID']}"
        
        if current_problem['문제유형'] == '객관식':
            options = []
            for i in range(1, 6):
                option_key = f'보기{i}'
                if option_key in current_problem and current_problem[option_key]:
                    options.append(current_problem[option_key])
            
            user_answer = st.radio(
                "답을 선택하세요:", 
                options, 
                key=answer_key,
                index=options.index(st.session_state.answers.get(current_problem['문제ID'], "")) if current_problem['문제ID'] in st.session_state.answers and st.session_state.answers[current_problem['문제ID']] in options else 0
            )
        else:
            user_answer = st.text_input(
                "답을 입력하세요:", 
                key=answer_key,
                value=st.session_state.answers.get(current_problem['문제ID'], "")
            )
        
        # 답변 저장
        st.session_state.answers[current_problem['문제ID']] = user_answer
        
        # 이전/다음 버튼
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if current_index > 0 and st.button("이전", key="prev_btn"):
                st.session_state.current_problem_index -= 1
                st.rerun()
        
        with col2:
            if current_index < total_problems - 1 and st.button("다음", key="next_btn"):
                st.session_state.current_problem_index += 1
                st.rerun()
        
        # 제출 버튼 (마지막 문제이거나 시간 종료 시)
        with col3:
            if (current_index == total_problems - 1 or st.session_state.time_expired) and st.button("제출하기", key="submit_btn", type="primary"):
                # 모든 답변 채점 및 저장
                results = []
                total_score = 0
                
                for problem in st.session_state.custom_problems:
                    problem_id = problem['문제ID']
                    user_answer = st.session_state.answers.get(problem_id, "")
                    
                    # 채점
                    score, feedback = grade_answer(
                        problem['문제유형'],
                        problem['정답'],
                        user_answer,
                        problem.get('키워드', '')
                    )
                    
                    # 결과 저장
                    result = {
                        '학생ID': student_id,
                        '이름': student_name,
                        '학년': student_grade,
                        '문제ID': problem_id,
                        '제출답안': user_answer,
                        '점수': score,
                        '피드백': feedback,
                        '제출시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    save_answer(service, spreadsheet_id, result)
                    results.append(result)
                    total_score += score
                
                st.session_state.quiz_completed = True
                st.session_state.quiz_results = results
                st.session_state.quiz_total_score = total_score / len(st.session_state.custom_problems)
                
                st.rerun()
    
    elif st.session_state.quiz_completed:
        st.subheader("테스트 결과")
        
        # 테스트 결과 표시
        st.write(f"총점: {st.session_state.quiz_total_score:.1f}점")
        
        # 걸린 시간 계산
        elapsed_time = datetime.now() - st.session_state.start_time
        minutes, seconds = divmod(int(elapsed_time.total_seconds()), 60)
        st.write(f"소요 시간: {minutes}분 {seconds}초")
        
        # 결과 테이블
        results_df = pd.DataFrame(st.session_state.quiz_results)
        
        # 정답률 계산
        correct_count = len([r for r in st.session_state.quiz_results if r['점수'] >= 80])
        incorrect_count = len(st.session_state.quiz_results) - correct_count
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"맞은 문제: {correct_count}문제")
        with col2:
            st.write(f"틀린 문제: {incorrect_count}문제")
        
        # 결과 표시
        st.subheader("상세 결과")
        
        for i, problem in enumerate(st.session_state.custom_problems):
            with st.expander(f"{i+1}. {problem['문제내용']}"):
                result = next((r for r in st.session_state.quiz_results if r['문제ID'] == problem['문제ID']), None)
                
                if result:
                    st.write(f"**제출 답안:** {result['제출답안']}")
                    st.write(f"**정답:** {problem['정답']}")
                    st.write(f"**점수:** {result['점수']}점")
                    st.write(f"**피드백:** {result['피드백']}")
                    
                    if result['점수'] < 100:
                        st.write(f"**해설:** {problem['해설']}")
        
        if st.button("새로운 테스트 시작"):
            # 상태 초기화
            st.session_state.quiz_started = False
            st.session_state.quiz_completed = False
            st.session_state.custom_problems = []
            st.rerun()

if __name__ == "__main__":
    run_timed_quiz() 