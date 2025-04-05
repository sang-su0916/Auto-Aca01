import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import time
import os
import json

# Google Sheets API 임포트 오류 처리
try:
    from sheets.google_sheets import GoogleSheetsAPI
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    st.error("Google Sheets API 관련 패키지가 설치되지 않았습니다. 로컬 모드로 실행합니다.")

# 페이지 설정
st.set_page_config(
    page_title="학원 자동 첨삭 시스템",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 로그인 화면에서 사이드바 숨김
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# 사용자 정보
USER_DB = {
    "admin": {"password": "1234", "name": "관리자", "role": "teacher", "grade": ""},
    "student1": {"password": "1234", "name": "홍길동", "role": "student", "grade": "중3"},
    "student2": {"password": "1234", "name": "김철수", "role": "student", "grade": "중2"},
    "student3": {"password": "1234", "name": "박영희", "role": "student", "grade": "중1"}
}

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'current_problem_index' not in st.session_state:
    st.session_state.current_problem_index = 0
if 'problems' not in st.session_state:
    st.session_state.problems = None
if 'student_answers' not in st.session_state:
    st.session_state.student_answers = None
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = "collapsed"

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
    
    # Google Sheets API 사용 가능 여부 확인
    if GOOGLE_SHEETS_AVAILABLE and os.path.exists('credentials.json') and 'GOOGLE_SHEETS_SPREADSHEET_ID' in os.environ:
        try:
            sheets_api = GoogleSheetsAPI()
            # 문제 데이터 로드
            problems = sheets_api.get_problems()
            st.session_state.problems = problems
            
            # 학생 답변 데이터 로드
            student_answers = sheets_api.get_student_answers()
            st.session_state.student_answers = student_answers
            
            return True
        except Exception as e:
            st.error(f"Google Sheets API 연결 오류: {str(e)}")
            # 오류 발생 시 로컬 파일 사용
            st.warning("로컬 CSV 파일로 대체합니다.")
    
    # 로컬 CSV 파일 사용
    try:
        # 문제 데이터 로드
        problems_df = pd.read_csv(PROBLEMS_CSV)
        st.session_state.problems = problems_df.to_dict('records')
        
        # 학생 답변 데이터 로드
        student_answers_df = pd.read_csv(STUDENT_ANSWERS_CSV)
        st.session_state.student_answers = student_answers_df.to_dict('records')
        
        return True
    except Exception as e:
        st.error(f"로컬 CSV 파일 로드 오류: {str(e)}")
        return False

# 문제 채점 함수
def grade_answer(problem_type, correct_answer, user_answer, keywords=None):
    if problem_type == '객관식':
        is_correct = user_answer.strip() == correct_answer.strip()
        score = 100 if is_correct else 0
        feedback = "정답입니다!" if is_correct else f"오답입니다. 정답은 '{correct_answer}'입니다."
    else:  # 주관식
        if not keywords:
            # 키워드가 없을 경우 정확히 일치하는지 확인
            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
            score = 100 if is_correct else 0
            feedback = "정답입니다!" if is_correct else f"오답입니다. 정답 예시: '{correct_answer}'"
        else:
            # 키워드 기반 채점
            keywords_list = [k.strip().lower() for k in keywords.split(',')]
            user_answer_lower = user_answer.strip().lower()
            
            matched_keywords = [k for k in keywords_list if k in user_answer_lower]
            if matched_keywords:
                score = min(100, int(len(matched_keywords) / len(keywords_list) * 100))
                if score >= 80:
                    feedback = "정답입니다! 필요한 키워드를 모두 포함했습니다."
                elif score >= 50:
                    feedback = f"부분 정답입니다. 다음 키워드가 포함되었습니다: {', '.join(matched_keywords)}"
                else:
                    feedback = f"아쉽습니다. 일부 키워드만 포함되었습니다: {', '.join(matched_keywords)}"
            else:
                score = 0
                feedback = f"오답입니다. 다음 키워드 중 일부를 포함해야 합니다: {', '.join(keywords_list[:2])}"
    
    return {"score": score, "feedback": feedback}

# 학생 답변 저장 함수
def save_student_answer(student_id, name, grade, problem_id, answer, score, feedback):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 답변 저장
    new_answer = {
        '학생ID': student_id,
        '이름': name,
        '학년': grade,
        '문제ID': problem_id,
        '제출답안': answer,
        '점수': score,
        '피드백': feedback,
        '제출시간': now
    }
    
    # 로컬 변수에 추가
    if st.session_state.student_answers is None:
        st.session_state.student_answers = []
    st.session_state.student_answers.append(new_answer)
    
    # Google Sheets API 사용 가능한 경우
    if GOOGLE_SHEETS_AVAILABLE and os.path.exists('credentials.json') and 'GOOGLE_SHEETS_SPREADSHEET_ID' in os.environ:
        try:
            sheets_api = GoogleSheetsAPI()
            sheets_api.add_student_answer(new_answer)
        except Exception as e:
            st.error(f"Google Sheets API 저장 오류: {str(e)}")
            # 오류 발생 시 로컬 파일에 저장
            save_to_local_csv(new_answer)
    else:
        # 로컬 CSV 파일에 저장
        save_to_local_csv(new_answer)
    
    return {"submitted_at": now}

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
        st.session_state.user_data = {
            "username": username,
            "name": USER_DB[username]["name"],
            "role": USER_DB[username]["role"],
            "grade": USER_DB[username]["grade"]
        }
        load_data()  # 데이터 로드
        return True
    return False

# 로그아웃 함수
def logout():
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.session_state.current_problem_index = 0

# 다음 문제 버튼 핸들러
def next_problem():
    if st.session_state.current_problem_index < len(st.session_state.problems) - 1:
        st.session_state.current_problem_index += 1

# 이전 문제 버튼 핸들러
def prev_problem():
    if st.session_state.current_problem_index > 0:
        st.session_state.current_problem_index -= 1

# 교사용 대시보드
def teacher_dashboard():
    st.title("👨‍🏫 교사 대시보드")
    
    tab1, tab2, tab3 = st.tabs(["문제 관리", "학생 답안 확인", "통계 분석"])
    
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
        st.header("학생 답안 확인")
        
        # 학생 답변 목록 표시
        if st.session_state.student_answers:
            student_answers_df = pd.DataFrame(st.session_state.student_answers)
            st.dataframe(student_answers_df)
        else:
            st.info("제출된 학생 답안이 없습니다.")
    
    with tab3:
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

# 학생용 포털
def student_portal():
    st.title("👨‍🎓 학생 포털")
    
    user_data = st.session_state.user_data
    st.write(f"안녕하세요, {user_data['name']}님 ({user_data['grade']})")
    
    # 문제 풀기
    st.header("📝 문제 풀기")
    
    # 문제가 있는지 확인
    if not st.session_state.problems:
        st.warning("등록된 문제가 없습니다.")
        return
    
    # 현재 문제 인덱스
    current_index = st.session_state.current_problem_index
    total_problems = len(st.session_state.problems)
    
    # 현재 문제 표시
    problem = st.session_state.problems[current_index]
    
    # 학생이 이미 답변한 문제인지 확인
    already_answered = False
    previous_answer = ""
    previous_feedback = ""
    previous_score = 0
    
    if st.session_state.student_answers:
        for ans in st.session_state.student_answers:
            if (ans['학생ID'] == user_data['username'] and 
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
        
        user_answer = ""
        submit_pressed = False
        
        with st.form("answer_form"):
            # 객관식 문제
            if problem['문제유형'] == '객관식':
                options = [problem[f'보기{i+1}'] for i in range(5) if problem[f'보기{i+1}'] != '']
                
                if already_answered:
                    answer_idx = options.index(previous_answer) if previous_answer in options else 0
                    user_answer = st.radio(
                        "답안 선택:", options, index=answer_idx, disabled=True
                    )
                else:
                    user_answer = st.radio("답안 선택:", options)
            
            # 주관식 문제
            else:
                if already_answered:
                    user_answer = st.text_area("답안 작성:", value=previous_answer, disabled=True)
                else:
                    user_answer = st.text_area("답안 작성:")
            
            # 제출 버튼
            if already_answered:
                submit_button = st.form_submit_button("이미 제출한 문제입니다", disabled=True)
                
                # 이전 답변 결과 표시
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
            else:
                submit_button = st.form_submit_button("제출하기")
                
                if submit_button and user_answer:
                    submit_pressed = True
        
        # 제출 처리
        if submit_pressed:
            # 답안 채점
            grading_result = grade_answer(
                problem['문제유형'], 
                problem['정답'], 
                user_answer, 
                problem.get('키워드', '')
            )
            
            # 답안 저장
            save_student_answer(
                user_data['username'],
                user_data['name'],
                user_data['grade'],
                problem['문제ID'],
                user_answer,
                grading_result['score'],
                grading_result['feedback']
            )
            
            # 결과 표시
            if grading_result['score'] >= 80:
                st.success(f"점수: {grading_result['score']}점 - {grading_result['feedback']}")
            elif grading_result['score'] >= 50:
                st.warning(f"점수: {grading_result['score']}점 - {grading_result['feedback']}")
            else:
                st.error(f"점수: {grading_result['score']}점 - {grading_result['feedback']}")
            
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
    
    # 학생 성적 확인
    st.header("📊 나의 학습 현황")
    
    if st.session_state.student_answers:
        my_answers = [ans for ans in st.session_state.student_answers 
                    if ans['학생ID'] == user_data['username']]
        
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
            st.write(f"👤 {st.session_state.user_data['name']}")
            st.write(f"역할: {st.session_state.user_data['role']}")
            
            if st.button("로그아웃"):
                logout()
                st.rerun()
    
    # 메인 페이지
    if not st.session_state.authenticated:
        login()
    else:
        if st.session_state.user_data["role"] == "teacher":
            teacher_dashboard()
        else:
            student_portal()

if __name__ == "__main__":
    main() 