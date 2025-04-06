import streamlit as st

# 페이지 설정 - 반드시 다른 st 명령어보다 먼저 와야 함
st.set_page_config(
    page_title="학원 자동 첨삭 시스템",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import pandas as pd
import base64
from datetime import datetime
import time
import os
import json
import io
from dotenv import load_dotenv
from pathlib import Path
import random
# 로직 모듈 임포트
from logic.grader import Grader

# 환경 변수 파일을 직접 읽어서 처리
env_path = Path('.env')
if env_path.exists():
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    except Exception as e:
        st.error(f"환경 변수 파일 읽기 오류: {str(e)}")

# 사이드바 완전히 숨기기
st.markdown("""
<style>
    [data-testid="collapsedControl"] {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 로그인 화면에서 사이드바 숨김
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# 사용자 정보
USER_DB = {
    "admin": {"password": "1234", "name": "관리자", "role": "teacher", "grade": "선생님"},
    "student1": {"password": "1234", "name": "홍길동", "role": "student", "grade": "중3"},
    "student2": {"password": "1234", "name": "김철수", "role": "student", "grade": "중2"},
    "student3": {"password": "1234", "name": "박영희", "role": "student", "grade": "중1"}
}

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'grade' not in st.session_state:
    st.session_state.grade = ""
if 'problems' not in st.session_state:
    st.session_state.problems = []
if 'student_answers' not in st.session_state:
    st.session_state.student_answers = []
if 'current_problem_index' not in st.session_state:
    st.session_state.current_problem_index = 0

# 파일 경로
PROBLEMS_CSV = "sample_questions.csv"
STUDENT_ANSWERS_CSV = "student_answers.csv"

# CSV 파일 초기화
def initialize_csv_files():
    # 문제 CSV 파일 생성
    if not os.path.exists(PROBLEMS_CSV):
        problems_df = pd.DataFrame(columns=[
            '문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
            '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설'
        ])
        # 샘플 문제 데이터
        sample_problems = [
            {
                '문제ID': 'P001',
                '과목': '영어', 
                '학년': '중3', 
                '문제유형': '객관식', 
                '난이도': '중', 
                '문제내용': 'What is the capital of the UK?',
                '보기1': 'London', 
                '보기2': 'Paris', 
                '보기3': 'Berlin', 
                '보기4': 'Rome', 
                '보기5': '', 
                '정답': 'London', 
                '키워드': 'capital,UK,London',
                '해설': 'The capital city of the United Kingdom is London.'
            },
            {
                '문제ID': 'P002',
                '과목': '영어', 
                '학년': '중3', 
                '문제유형': '주관식', 
                '난이도': '중', 
                '문제내용': 'Write a sentence using the word "beautiful".',
                '보기1': '', 
                '보기2': '', 
                '보기3': '', 
                '보기4': '', 
                '보기5': '', 
                '정답': 'The flower is beautiful.', 
                '키워드': 'beautiful,sentence',
                '해설': '주어와 동사를 포함한 완전한 문장이어야 합니다.'
            }
        ]
        for sample in sample_problems:
            problems_df = pd.concat([problems_df, pd.DataFrame([sample])], ignore_index=True)
        problems_df.to_csv(PROBLEMS_CSV, index=False)
    
    # 학생 답변 CSV 파일 생성
    if not os.path.exists(STUDENT_ANSWERS_CSV):
        student_answers_df = pd.DataFrame(columns=[
            '학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간'
        ])
        student_answers_df.to_csv(STUDENT_ANSWERS_CSV, index=False)

# 데이터 로드 함수
def load_data():
    initialize_csv_files()
    
    # 구글 시트 API 연동 시도
    GOOGLE_SHEETS_AVAILABLE = False
    try:
        # 필요한 환경 변수 확인
        if not os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'):
            st.warning("환경 변수 'GOOGLE_SHEETS_SPREADSHEET_ID'가 설정되지 않았습니다.")
            st.info("로컬 CSV 파일로 대체합니다.")
        elif not os.path.exists('credentials.json'):
            st.warning("인증 파일 'credentials.json'이 존재하지 않습니다.")
            st.info("로컬 CSV 파일로 대체합니다.")
        else:
            from sheets.google_sheets import GoogleSheetsAPI
            # API 초기화 시도
            try:
                sheets_api = GoogleSheetsAPI()
                if sheets_api.is_connected():
                    GOOGLE_SHEETS_AVAILABLE = True
                    st.session_state.sheets_api = sheets_api  # 세션에 API 객체 저장
                    st.success("Google Sheets API가 성공적으로 연결되었습니다.")
                else:
                    st.warning("Google Sheets API 연결 실패: API 서비스가 초기화되지 않았습니다.")
            except Exception as e:
                st.warning(f"Google Sheets API 연결 실패: {str(e)}")
    except ImportError as e:
        st.warning(f"Google API 패키지가 설치되지 않았습니다. 로컬 모드로 실행됩니다. 오류: {str(e)}")
    
    # 구글 시트에서 데이터 로드 시도
    if GOOGLE_SHEETS_AVAILABLE and 'sheets_api' in st.session_state:
        try:
            sheets_api = st.session_state.sheets_api
            
            # 학생 답변 데이터 로드
            student_answers = sheets_api.get_student_answers()
            if student_answers:
                st.session_state.student_answers = student_answers
                st.success(f"구글 시트에서 {len(student_answers)}개의 학생 답변을 가져왔습니다.")
            
            # 사용자 역할과 학년에 따라 오늘의 문제 로드
            if st.session_state.role == 'student':
                # 학생인 경우 해당 학년의 오늘 문제만 가져오기
                daily_problems = sheets_api.get_daily_problems(grade=st.session_state.grade)
                if daily_problems:
                    st.session_state.problems = daily_problems
                    st.success(f"오늘의 {st.session_state.grade} 문제 {len(daily_problems)}개를 가져왔습니다.")
            else:
                # 교사인 경우 모든 문제 가져오기
                problems = sheets_api.get_problems()
                if problems:
                    st.session_state.problems = problems
                    st.success(f"구글 시트에서 {len(problems)}개의 문제를 가져왔습니다.")
            
            return True
        except Exception as e:
            st.error(f"Google Sheets API 연결 오류: {str(e)}")
            st.warning("로컬 CSV 파일로 대체합니다.")
    
    # 로컬 CSV 파일 사용
    try:
        # 문제 데이터 로드
        problems_df = pd.read_csv(PROBLEMS_CSV)
        st.session_state.problems = problems_df.to_dict('records')
        st.info(f"로컬 CSV 파일에서 {len(st.session_state.problems)}개의 문제를 로드했습니다.")
        
        # 학생 답변 데이터 로드
        student_answers_df = pd.read_csv(STUDENT_ANSWERS_CSV)
        st.session_state.student_answers = student_answers_df.to_dict('records')
        
        return True
    except Exception as e:
        st.error(f"로컬 CSV 파일 로드 오류: {str(e)}")
        return False

# 문제 채점 함수
def grade_answer(problem_type, correct_answer, user_answer, keywords=None):
    grader = Grader()
    return grader.grade_answer(problem_type, correct_answer, user_answer, keywords)

# 학생 답변 저장 함수
def save_student_answer(student_id, name, grade, problem_id, answer, score, feedback):
    # 현재 시간 기록
    submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 학생 답변 데이터 구성
    new_answer = {
        '학생ID': student_id,
        '이름': name,
        '학년': grade,
        '문제ID': problem_id,
        '제출답안': answer,
        '점수': score,
        '피드백': feedback,
        '제출시간': submission_time
    }
    
    # 세션 상태에 추가
    st.session_state.student_answers.append(new_answer)
    
    # Google Sheets API가 있으면 저장
    if 'sheets_api' in st.session_state:
        try:
            sheets_api = st.session_state.sheets_api
            # API로 학생 답변 저장
            sheets_api.save_student_answer(new_answer)
            return True
        except Exception as e:
            st.error(f"Google Sheets에 저장 실패: {str(e)}")
    
    # 로컬 CSV 파일에 저장
    save_to_local_csv(new_answer)
    return True

# 로컬 CSV 파일에 학생 답변 저장
def save_to_local_csv(new_answer):
    try:
        # 기존 데이터 로드
        df = pd.read_csv(STUDENT_ANSWERS_CSV)
        # 새 데이터 추가
        df = pd.concat([df, pd.DataFrame([new_answer])], ignore_index=True)
        # 파일에 저장
        df.to_csv(STUDENT_ANSWERS_CSV, index=False)
    except Exception as e:
        st.error(f"로컬 파일 저장 오류: {str(e)}")

# 인증 함수
def authenticate_user(username, password):
    if username in USER_DB and USER_DB[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.name = USER_DB[username]["name"]
        st.session_state.role = USER_DB[username]["role"]
        st.session_state.grade = USER_DB[username]["grade"]
        load_data()  # 데이터 로드
        return True
    return False

# 로그아웃 함수
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.name = ""
    st.session_state.role = ""
    st.session_state.grade = ""
    st.session_state.problems = []
    st.session_state.student_answers = []

# 다음 문제로 이동하는 함수
def next_problem():
    if st.session_state.current_problem_index < len(st.session_state.problems) - 1:
        st.session_state.current_problem_index += 1

# 이전 문제로 이동하는 함수
def prev_problem():
    if st.session_state.current_problem_index > 0:
        st.session_state.current_problem_index -= 1

# 로컬 CSV 파일에 문제 저장
def save_problem_to_local_csv(new_problem):
    try:
        # 기존 데이터 로드
        df = pd.read_csv(PROBLEMS_CSV)
        # 새 데이터 추가
        df = pd.concat([df, pd.DataFrame([new_problem])], ignore_index=True)
        # 파일에 저장
        df.to_csv(PROBLEMS_CSV, index=False)
    except Exception as e:
        st.error(f"로컬 파일 저장 오류: {str(e)}")

# 교사용 대시보드
def teacher_dashboard():
    st.title("👨‍🏫 교사 대시보드")
    
    tab1, tab2, tab3, tab4 = st.tabs(["문제 관리", "일일/주간 문제", "학생 답안 확인", "통계 분석"])
    
    with tab1:
        st.header("문제 관리")
        
        # 문제 목록 표시
        if st.session_state.problems:
            problems_df = pd.DataFrame(st.session_state.problems)
            st.dataframe(problems_df)
        else:
            st.info("등록된 문제가 없습니다.")
        
        # 새 문제 등록 폼
        with st.expander("새 문제 등록", expanded=False):
            with st.form("new_problem_form"):
                problem_id = st.text_input("문제 ID", value=f"P{len(st.session_state.problems)+1:03d}")
                subject = st.text_input("과목", value="영어")
                grade = st.selectbox("학년", ["중1", "중2", "중3", "고1", "고2", "고3"])
                problem_type = st.selectbox("문제 유형", ["객관식", "주관식"])
                difficulty = st.selectbox("난이도", ["하", "중", "상"])
                content = st.text_area("문제 내용")
                
                # 객관식일 경우 보기 추가
                options = [""] * 5
                if problem_type == "객관식":
                    for i in range(4):
                        options[i] = st.text_input(f"보기 {i+1}")
                
                answer = st.text_input("정답")
                keywords = st.text_input("키워드 (쉼표로 구분)")
                explanation = st.text_area("해설")
                
                submit_button = st.form_submit_button("문제 등록")
                
                if submit_button:
                    new_problem = {
                        '문제ID': problem_id,
                        '과목': subject,
                        '학년': grade,
                        '문제유형': problem_type,
                        '난이도': difficulty,
                        '문제내용': content,
                        '보기1': options[0],
                        '보기2': options[1],
                        '보기3': options[2],
                        '보기4': options[3],
                        '보기5': options[4],
                        '정답': answer,
                        '키워드': keywords,
                        '해설': explanation
                    }
                    
                    # 로컬 변수에 추가
                    if st.session_state.problems is None:
                        st.session_state.problems = []
                    st.session_state.problems.append(new_problem)
                    
                    # Google Sheets API 사용 가능한 경우
                    if GOOGLE_SHEETS_AVAILABLE and os.path.exists('credentials.json') and 'GOOGLE_SHEETS_SPREADSHEET_ID' in os.environ:
                        try:
                            sheets_api = GoogleSheetsAPI()
                            sheets_api.add_problem(new_problem)
                        except Exception as e:
                            st.error(f"Google Sheets API 저장 오류: {str(e)}")
                            # 오류 발생 시 로컬 파일에 저장
                            save_problem_to_local_csv(new_problem)
                    else:
                        # 로컬 CSV 파일에 저장
                        save_problem_to_local_csv(new_problem)
                    
                    st.success("새 문제가 등록되었습니다!")
    
    with tab2:
        st.header("일일/주간 문제 관리")
        
        # 구글 시트 연동 확인
        if hasattr(st.session_state, 'sheets_api'):
            subtab1, subtab2 = st.tabs(["오늘의 문제", "주간 계획"])
            
            with subtab1:
                st.subheader("오늘의 문제 확인")
                
                grade_filter = st.selectbox(
                    "학년 선택",
                    ["전체", "중1", "중2", "중3", "고1", "고2", "고3"],
                    key="daily_grade_select"
                )
                
                selected_grade = None if grade_filter == "전체" else grade_filter
                
                # 오늘의 문제 가져오기
                if st.button("오늘의 문제 확인하기"):
                    daily_problems = st.session_state.sheets_api.get_daily_problems(grade=selected_grade)
                    if daily_problems:
                        st.success(f"오늘의 {selected_grade if selected_grade else '전체'} 문제 {len(daily_problems)}개를 가져왔습니다.")
                        st.dataframe(pd.DataFrame(daily_problems))
                    else:
                        st.warning(f"{selected_grade if selected_grade else '전체'} 학년에 해당하는 문제가 없습니다.")
            
            with subtab2:
                st.subheader("주간 문제 계획")
                
                col1, col2 = st.columns(2)
                with col1:
                    plan_grade = st.selectbox(
                        "학년 선택",
                        ["전체", "중1", "중2", "중3", "고1", "고2", "고3"],
                        key="weekly_grade_select"
                    )
                with col2:
                    days_count = st.slider("계획할 일수", min_value=1, max_value=14, value=7)
                
                selected_plan_grade = None if plan_grade == "전체" else plan_grade
                
                # 주간 계획 생성하기
                if st.button("주간 계획 생성하기"):
                    weekly_problems = st.session_state.sheets_api.get_weekly_problems(
                        grade=selected_plan_grade, 
                        problems_per_day=20,
                        days=days_count
                    )
                    
                    if weekly_problems:
                        st.success(f"{days_count}일간의 문제 계획이 생성되었습니다.")
                        
                        # 각 날짜별로 탭 생성
                        date_tabs = st.tabs(list(weekly_problems.keys()))
                        
                        for i, date in enumerate(weekly_problems.keys()):
                            with date_tabs[i]:
                                st.write(f"**{date}의 문제 ({len(weekly_problems[date])}개)**")
                                
                                # 해당 날짜의 문제 표시
                                date_problems_df = pd.DataFrame(weekly_problems[date])
                                st.dataframe(date_problems_df)
                    else:
                        st.warning("주간 계획을 생성할 수 없습니다.")
        else:
            st.warning("이 기능을 사용하려면 Google Sheets API 연동이 필요합니다.")
    
    with tab3:
        st.header("학생 답안 확인")
        
        # 학생 답변 목록 표시
        if st.session_state.student_answers:
            student_answers_df = pd.DataFrame(st.session_state.student_answers)
            st.dataframe(student_answers_df)
        else:
            st.info("제출된 학생 답안이 없습니다.")
    
    with tab4:
        st.header("통계 분석")
        
        if st.session_state.student_answers:
            student_answers_df = pd.DataFrame(st.session_state.student_answers)
            
            # 전체 평균 점수
            avg_score = student_answers_df['점수'].mean()
            st.metric("전체 평균 점수", f"{avg_score:.1f}점")
            
            # 문제별 평균 점수
            st.subheader("문제별 평균 점수")
            problem_avg = student_answers_df.groupby('문제ID')['점수'].mean().reset_index()
            problem_avg.columns = ['문제 ID', '평균 점수']
            st.bar_chart(problem_avg.set_index('문제 ID'))
            
            # 학생별 평균 점수
            st.subheader("학생별 평균 점수")
            student_avg = student_answers_df.groupby(['이름', '학년'])['점수'].mean().reset_index()
            student_avg.columns = ['학생 이름', '학년', '평균 점수']
            st.dataframe(student_avg)
        else:
            st.info("통계를 생성할 데이터가 없습니다.")

# 학생용 포털
def student_portal():
    st.title("👨‍🎓 학생 포털")
    
    st.write(f"안녕하세요, {st.session_state.name}님 ({st.session_state.grade})")
    
    # 오늘의 문제 표시
    today = datetime.now().strftime('%Y-%m-%d')
    st.header(f"📝 {today} 오늘의 문제")
    
    # 문제 데이터 확인 및 새로 가져오기
    if not st.session_state.problems:
        if hasattr(st.session_state, 'sheets_api'):
            # 학생 학년에 맞는 오늘의 문제 20개 가져오기
            daily_problems = st.session_state.sheets_api.get_daily_problems(grade=st.session_state.grade)
            if daily_problems:
                st.session_state.problems = daily_problems
                st.success(f"오늘의 {st.session_state.grade} 문제 {len(daily_problems)}개를 가져왔습니다.")
            else:
                st.warning("오늘의 문제를 가져올 수 없습니다.")
                return
        else:
            st.warning("등록된 문제가 없습니다.")
            return
    
    # 문제 필터링 (학생 학년에 맞는 문제만)
    if hasattr(st.session_state, 'sheets_api') and st.session_state.grade:
        filtered_problems = [p for p in st.session_state.problems if p.get('학년', '') == st.session_state.grade]
        if filtered_problems:
            st.session_state.problems = filtered_problems
    
    # 현재 문제 인덱스
    current_index = st.session_state.current_problem_index
    total_problems = len(st.session_state.problems)
    
    # 현재 문제가 유효한지 확인
    if current_index >= total_problems:
        st.session_state.current_problem_index = 0
        current_index = 0
    
    # 문제 진행률 표시
    st.progress((current_index + 1) / total_problems)
    st.write(f"문제 {current_index + 1}/{total_problems}")
    
    # 모든 문제의 답변을 저장할 세션 상태 변수 초기화
    if 'all_answers' not in st.session_state:
        st.session_state.all_answers = [""] * total_problems
    
    # 현재 문제 표시
    problem = st.session_state.problems[current_index]
    
    # 학생이 이미 답변한 문제인지 확인
    already_answered = False
    previous_answer = ""
    previous_feedback = ""
    previous_score = 0
    
    if st.session_state.student_answers:
        for ans in st.session_state.student_answers:
            if (ans['학생ID'] == st.session_state.username and 
                ans['문제ID'] == problem['문제ID']):
                already_answered = True
                previous_answer = ans['제출답안']
                previous_feedback = ans['피드백']
                previous_score = ans['점수']
                break
    
    # 문제 정보 표시
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.write(f"**문제 {current_index + 1}/{total_problems}**")
        st.write(f"**ID:** {problem['문제ID']} | **과목:** {problem['과목']} | **난이도:** {problem['난이도']}")
        st.write(f"**유형:** {problem['문제유형']}")
        
        st.markdown(f"### {problem['문제내용']}")
        
        # 답변 입력 폼 (제출 버튼은 마지막 문제에만 표시)
        is_last_problem = (current_index == total_problems - 1)
        
        # 객관식 문제
        if problem['문제유형'] == '객관식':
            options = []
            # 비어있지 않은 보기만 추가
            for i in range(5):
                option = problem.get(f'보기{i+1}', '')
                if option and option.strip():
                    options.append(option)
            
            # 이전/다음 문제의 정답을 보기에 추가하여 겹치게 만들기
            prev_answer = None
            next_answer = None
            
            # 이전 문제의 정답 가져오기
            if current_index > 0:
                prev_problem = st.session_state.problems[current_index - 1]
                if prev_problem['문제유형'] == '객관식':
                    prev_answer = prev_problem.get('정답', '')
                    if prev_answer and prev_answer not in options:
                        options.append(prev_answer)
            
            # 다음 문제의 정답 가져오기
            if current_index < total_problems - 1:
                next_problem = st.session_state.problems[current_index + 1]
                if next_problem['문제유형'] == '객관식':
                    next_answer = next_problem.get('정답', '')
                    if next_answer and next_answer not in options:
                        options.append(next_answer)
            
            # 옵션 섞기
            random.seed(problem['문제ID'])
            random.shuffle(options)
            
            if already_answered:
                answer_idx = options.index(previous_answer) if previous_answer in options else 0
                user_answer = st.radio(
                    "답안 선택:", options, index=answer_idx, disabled=True, key=f"radio_{current_index}"
                )
                st.session_state.all_answers[current_index] = user_answer
            else:
                # 사용자가 이전에 선택한 답변이 있는 경우 해당 옵션을 선택 상태로 표시
                default_index = 0
                if st.session_state.all_answers[current_index] in options:
                    default_index = options.index(st.session_state.all_answers[current_index])
                
                user_answer = st.radio(
                    "답안 선택:", options, index=default_index, key=f"radio_{current_index}"
                )
                st.session_state.all_answers[current_index] = user_answer
        
        # 주관식 문제
        else:
            if already_answered:
                user_answer = st.text_area("답안 작성:", value=previous_answer, disabled=True, key=f"text_{current_index}")
                st.session_state.all_answers[current_index] = user_answer
            else:
                user_answer = st.text_area("답안 작성:", value=st.session_state.all_answers[current_index], key=f"text_{current_index}")
                st.session_state.all_answers[current_index] = user_answer
        
        # 이미 답변한 문제에 대한 결과 표시
        if already_answered:
            st.info(f"제출한 답변: {previous_answer}")
            if previous_score >= 80:
                st.success(f"점수: {previous_score}점 - {previous_feedback}")
            elif previous_score >= 50:
                st.warning(f"점수: {previous_score}점 - {previous_feedback}")
            else:
                st.error(f"점수: {previous_score}점 - {previous_feedback}")
            
            if problem.get('해설'):
                with st.expander("해설 보기"):
                    st.write(problem['해설'])
    
    # 이전/다음 버튼
    col1, col2 = st.columns(2)
    with col1:
        if current_index > 0:
            if st.button("← 이전 문제"):
                prev_problem()
                st.rerun()
    with col2:
        if current_index < total_problems - 1:
            if st.button("다음 문제 →"):
                next_problem()
                st.rerun()
    
    # 마지막 문제에서만 제출 버튼 표시
    if is_last_problem:
        st.markdown("---")
        st.subheader("모든 문제 제출")
        
        if st.button("전체 문제 제출하기", type="primary"):
            # 모든 문제에 대한 답변 확인
            empty_answers = [i+1 for i, ans in enumerate(st.session_state.all_answers) if not ans]
            
            if empty_answers:
                st.error(f"다음 문제가 아직 답변되지 않았습니다: {', '.join(map(str, empty_answers))}")
            else:
                # 모든 답변 제출
                for i, problem in enumerate(st.session_state.problems):
                    # 이미 제출된 답변은 다시 제출하지 않음
                    already_submitted = False
                    if st.session_state.student_answers:
                        for ans in st.session_state.student_answers:
                            if (ans['학생ID'] == st.session_state.username and 
                                ans['문제ID'] == problem['문제ID']):
                                already_submitted = True
                                break
                    
                    if not already_submitted:
                        # 답안 채점
                        grading_result = grade_answer(
                            problem['문제유형'], 
                            problem['정답'], 
                            st.session_state.all_answers[i], 
                            problem.get('키워드', '')
                        )
                        
                        # 답안 저장
                        save_student_answer(
                            st.session_state.username,
                            st.session_state.name,
                            st.session_state.grade,
                            problem['문제ID'],
                            st.session_state.all_answers[i],
                            grading_result['score'],
                            grading_result['feedback']
                        )
                
                st.success("모든 문제가 성공적으로 제출되었습니다!")
                st.balloons()
                # 페이지 새로고침
                time.sleep(2)
                st.rerun()
    
    # 학생 성적 확인
    st.header("📊 나의 학습 현황")
    
    if st.session_state.student_answers:
        my_answers = [ans for ans in st.session_state.student_answers 
                    if ans['학생ID'] == st.session_state.username]
        
        if my_answers:
            my_answers_df = pd.DataFrame(my_answers)
            
            # 전체 평균 점수
            avg_score = my_answers_df['점수'].mean()
            total_solved = len(my_answers)
            total_problems = len(st.session_state.problems)
            progress = (total_solved / total_problems) * 100
            
            col1, col2, col3 = st.columns(3)
            col1.metric("푼 문제 수", f"{total_solved}/{total_problems}")
            col2.metric("진행률", f"{progress:.1f}%")
            col3.metric("평균 점수", f"{avg_score:.1f}점")
            
            # 제출 답안 기록
            st.subheader("나의 제출 기록")
            display_df = my_answers_df[['문제ID', '제출답안', '점수', '피드백', '제출시간']]
            st.dataframe(display_df)
        else:
            st.info("아직 제출한 답안이 없습니다.")
    else:
        st.info("아직 제출한 답안이 없습니다.")

# 로그인 화면
def login():
    st.title("🏫 학원 자동 첨삭 시스템")
    st.write("학생들의 영어 문제 풀이를 자동으로 채점하고 피드백을 제공합니다.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("로그인")
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        
        if st.button("로그인"):
            if authenticate_user(username, password):
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
        
        # 기본 계정 안내
        st.markdown("---")
        st.markdown("### 기본 계정")
        st.markdown("- 교사: `admin` / `1234` (관리자, 선생님)")
        st.markdown("- 학생1: `student1` / `1234` (홍길동, 중3)")
        st.markdown("- 학생2: `student2` / `1234` (김철수, 중2)")
        st.markdown("- 학생3: `student3` / `1234` (박영희, 중1)")

# 메인 함수
def main():
    # 초기 설정 확인
    initialize_csv_files()
    
    # 사이드바
    if st.session_state.authenticated:
        with st.sidebar:
            st.write(f"👤 {st.session_state.name}")
            st.write(f"역할: {st.session_state.role}")
            
            if st.button("로그아웃"):
                logout()
                st.rerun()
    
    # 메인 페이지
    if not st.session_state.authenticated:
        login()
    else:
        if st.session_state.role == "teacher":
            teacher_dashboard()
        else:
            student_portal()

if __name__ == "__main__":
    main() 