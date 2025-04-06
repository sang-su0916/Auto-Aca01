import streamlit as st
import sys
import os
import pandas as pd
import datetime
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.sheets.google_sheets import GoogleSheetsManager
from src.logic.grader import Grader, AutoGrader

def initialize_session_state():
    """세션 상태 초기화"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'student_id' not in st.session_state:
        st.session_state.student_id = ""
    if 'selected_problem' not in st.session_state:
        st.session_state.selected_problem = None
    if 'problems' not in st.session_state:
        st.session_state.problems = []
    if 'sheets_manager' not in st.session_state:
        # 기본 credentials.json 위치 (나중에 환경 변수로 설정 가능)
        credentials_path = 'credentials.json'
        spreadsheet_id = os.getenv('SPREADSHEET_ID', None)
        
        # Google Sheets 연결 초기화
        st.session_state.sheets_manager = GoogleSheetsManager(
            credentials_path=credentials_path,
            spreadsheet_id=spreadsheet_id
        )
    if 'grader' not in st.session_state:
        st.session_state.grader = AutoGrader()

def login_form():
    """학생 로그인 폼"""
    st.header("📝 학생 로그인")
    
    with st.form("login_form"):
        name = st.text_input("이름")
        student_id = st.text_input("학번")
        submitted = st.form_submit_button("로그인")
        
        if submitted:
            if name and student_id:
                st.session_state.logged_in = True
                st.session_state.student_name = name
                st.session_state.student_id = student_id
                st.success(f"{name}님, 환영합니다!")
                st.experimental_rerun()
            else:
                st.error("이름과 학번을 모두 입력해주세요.")

def load_problems():
    """Google Sheets에서 문제 목록 로드"""
    try:
        problems = st.session_state.sheets_manager.get_problems()
        st.session_state.problems = problems
        return problems
    except Exception as e:
        st.error(f"문제 로드 오류: {e}")
        return []

def display_problem_selection():
    """문제 선택 인터페이스"""
    st.header("🧩 문제 선택")
    
    # 문제 로드
    problems = load_problems()
    if not problems:
        st.warning("문제가 로드되지 않았습니다. 연결 상태를 확인해주세요.")
        return
    
    # 난이도별 문제 필터링
    difficulties = sorted(list(set(p.get("난이도", "중") for p in problems)))
    selected_difficulty = st.selectbox("난이도 선택", difficulties)
    
    filtered_problems = [p for p in problems if p.get("난이도", "중") == selected_difficulty]
    
    # 문제 목록 표시
    if filtered_problems:
        problem_titles = [f"{p['문제ID']} - {p['문제'][:30]}..." for p in filtered_problems]
        selected_problem_index = st.selectbox(
            "문제 선택", 
            range(len(problem_titles)),
            format_func=lambda i: problem_titles[i]
        )
        
        if st.button("문제 풀기"):
            st.session_state.selected_problem = filtered_problems[selected_problem_index]
            st.experimental_rerun()
    else:
        st.info(f"{selected_difficulty} 난이도의 문제가 없습니다.")

def display_problem_solving():
    """문제 풀이 인터페이스"""
    problem = st.session_state.selected_problem
    
    st.header("📝 문제 풀이")
    
    # 문제 정보 표시
    st.subheader(f"문제 ID: {problem['문제ID']} (난이도: {problem['난이도']})")
    st.markdown(problem['문제'])
    
    # 답안 제출 폼
    with st.form("answer_form"):
        answer = st.text_area("답안 작성", height=200)
        submitted = st.form_submit_button("제출하기")
        
        if submitted:
            if answer.strip():
                submit_answer(problem, answer)
            else:
                st.error("답안을 입력해주세요.")

def submit_answer(problem, answer):
    """답안 제출 및 채점"""
    try:
        # 채점 수행
        keywords = problem.get("키워드", [])
        model_answer = problem.get("모범답안", "")
        difficulty = problem.get("난이도", "중")
        
        # AutoGrader 사용 (상속받은 Grader 클래스의 인터페이스와 동일)
        score, feedback = st.session_state.grader.grade_answer(
            answer=answer,
            model_answer=model_answer,
            keywords=keywords,
            difficulty=difficulty
        )
        
        # 결과 Google Sheets에 저장
        sheets_manager = st.session_state.sheets_manager
        sheets_manager.add_student_answer(
            name=st.session_state.student_name,
            student_id=st.session_state.student_id,
            problem_id=problem["문제ID"],
            answer=answer,
            score=str(score),
            feedback=feedback
        )
        
        # 결과 표시
        st.success("답안이 제출되었습니다!")
        display_result(answer, score, feedback)
        
        # 새 문제 선택 버튼
        if st.button("다른 문제 풀기"):
            st.session_state.selected_problem = None
            st.experimental_rerun()
            
    except Exception as e:
        st.error(f"답안 제출 오류: {e}")

def display_result(answer, score, feedback):
    """채점 결과 표시"""
    st.subheader("📊 채점 결과")
    
    # 결과 카드 표시
    col1, col2 = st.columns(2)
    with col1:
        st.metric("점수", f"{score}/100")
    with col2:
        # 점수에 따른 색상 표시
        if score >= 90:
            st.markdown(f"<span style='color:green'>우수</span>", unsafe_allow_html=True)
        elif score >= 70:
            st.markdown(f"<span style='color:blue'>양호</span>", unsafe_allow_html=True)
        elif score >= 50:
            st.markdown(f"<span style='color:orange'>보통</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:red'>미흡</span>", unsafe_allow_html=True)
    
    # 피드백 표시
    st.subheader("🧐 피드백")
    st.write(feedback)
    
    # 제출한 답안 표시
    st.subheader("📝 제출한 답안")
    st.text_area("", answer, height=150, disabled=True)

def display_student_history():
    """학생 제출 기록 표시"""
    if not st.session_state.logged_in:
        return
        
    st.header("📚 나의 제출 기록")
    
    try:
        # 현재 학생의 답안 기록 조회
        sheets_manager = st.session_state.sheets_manager
        student_answers = sheets_manager.get_student_answers(
            student_name=st.session_state.student_name,
            student_id=st.session_state.student_id
        )
        
        if not student_answers:
            st.info("아직 제출한 답안이 없습니다.")
            return
            
        # 데이터프레임으로 변환하여 표시
        df = pd.DataFrame(student_answers)
        
        # 컬럼 순서 및 표시 설정
        df = df[['문제ID', '점수', '제출시간']]
        
        # 데이터프레임 표시
        st.dataframe(df)
        
        # 성적 통계
        avg_score = df['점수'].astype(float).mean()
        max_score = df['점수'].astype(float).max()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("평균 점수", f"{avg_score:.1f}")
        with col2:
            st.metric("최고 점수", f"{max_score:.1f}")
        
    except Exception as e:
        st.error(f"기록 조회 오류: {e}")

def main():
    """메인 함수"""
    st.title("🏫 학원 자동 첨삭 시스템 - 학생 포털")
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 사이드바에 학생 정보 표시
    with st.sidebar:
        if st.session_state.logged_in:
            st.success(f"로그인: {st.session_state.student_name} ({st.session_state.student_id})")
            if st.button("로그아웃"):
                # 세션 상태 초기화
                for key in list(st.session_state.keys()):
                    if key not in ['sheets_manager', 'grader']:
                        del st.session_state[key]
                st.experimental_rerun()
        else:
            st.info("로그인이 필요합니다.")
    
    # 로그인 상태에 따른 화면 표시
    if not st.session_state.logged_in:
        login_form()
    else:
        # 탭 구성: 문제 풀기 / 제출 기록
        tab1, tab2 = st.tabs(["문제 풀기", "제출 기록"])
        
        with tab1:
            if st.session_state.selected_problem:
                display_problem_solving()
            else:
                display_problem_selection()
        
        with tab2:
            display_student_history()

if __name__ == "__main__":
    main() 