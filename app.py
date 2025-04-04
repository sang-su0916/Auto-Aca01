import streamlit as st
import os
import pandas as pd
import base64
from datetime import datetime
import time
import json
from sheets.google_sheets import GoogleSheetsAPI

# 환경 변수 설정 (Streamlit Cloud 배포용)
from sheets.setup_env import setup_credentials, get_spreadsheet_id
setup_credentials()

# Google Sheets API 사용 여부 설정
USE_GOOGLE_SHEETS = True

# Google Sheets API가 사용 가능한 경우 모듈 임포트 시도
if USE_GOOGLE_SHEETS:
    try:
        sheets_api = GoogleSheetsAPI()
        SHEETS_AVAILABLE = True
    except Exception as e:
        st.error(f"Google Sheets API 연결 오류: {str(e)}")
        st.error("Google 모듈이 설치되어 있지 않거나 인증 파일이 없습니다.")
        st.error("다음 명령어로 필요한 패키지를 설치하세요: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        SHEETS_AVAILABLE = False
else:
    SHEETS_AVAILABLE = False

# CSV 파일 기반 백업 데이터
def load_csv_data():
    try:
        problems_df = pd.read_csv('sample_questions.csv', encoding='utf-8')
        student_answers_df = pd.DataFrame(columns=[
            '학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간'
        ])
        if os.path.exists('student_answers.csv'):
            student_answers_df = pd.read_csv('student_answers.csv', encoding='utf-8')
        return problems_df, student_answers_df
    except Exception as e:
        st.error(f"CSV 파일 로드 오류: {str(e)}")
        return None, None

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'show_sidebar' not in st.session_state:
    st.session_state.show_sidebar = False

# Hide sidebar by default
st.set_page_config(
    page_title="학원 자동 첨삭 시스템",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 사용자 계정 정보
def initialize_user_db():
    # users.json 파일이 있으면 로드, 없으면 기본값 사용
    if os.path.exists('users.json'):
        try:
            with open('users.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"사용자 데이터 파일 로드 오류: {str(e)}")
    
    # 기본 사용자 데이터
    default_users = {
        "admin": {
            "password": "1234",
            "name": "관리자",
            "role": "teacher",
            "grade": ""
        },
        "student1": {
            "password": "1234",
            "name": "홍길동",
            "role": "student",
            "grade": "중3"
        },
        "student2": {
            "password": "1234",
            "name": "김철수",
            "role": "student",
            "grade": "중2"
        }
    }
    return default_users

# 사용자 데이터베이스 로드
users_db = initialize_user_db()

# 자동 채점 기능
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

# Custom CSS to improve UI
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    /* Hide sidebar toggle by default */
    .css-1rs6os {
        visibility: hidden;
    }
    .css-1dp5vir {
        visibility: hidden;
    }
    .download-link {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .csv-guide {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .result-card {
        background-color: #f1f8e9;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .feedback-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #2196F3;
    }
</style>
""", unsafe_allow_html=True)

def teacher_dashboard():
    st.title("👨‍🏫 교사 대시보드")
    st.write("문제 관리 및 학생 성적 확인")
    
    tab1, tab2 = st.tabs(["문제 관리", "성적 통계"])
    
    with tab1:
        st.subheader("📝 문제 관리")
        
        # 기존 문제 표시
        if SHEETS_AVAILABLE:
            problems = sheets_api.get_problems()
            if problems:
                st.subheader("등록된 문제 목록")
                problems_df = pd.DataFrame(problems)
                st.dataframe(problems_df)
                st.success(f"총 {len(problems)}개의 문제가 등록되어 있습니다.")
            else:
                st.info("현재 등록된 문제가 없습니다.")
        else:
            problems_df, _ = load_csv_data()
            if problems_df is not None:
                st.subheader("로컬 CSV 문제 목록")
                st.dataframe(problems_df)
                st.success(f"총 {len(problems_df)}개의 문제가 로컬 CSV 파일에 있습니다.")
            else:
                st.info("현재 등록된 문제가 없습니다.")
        
        st.subheader("📝 새 문제 업로드")
        
        # 수동 문제 추가
        st.subheader("📝 문제 직접 추가")
        with st.form("add_problem_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                problem_id = st.text_input("문제ID", value="P" + datetime.now().strftime("%Y%m%d%H%M%S"))
                subject = st.selectbox("과목", ["영어", "수학", "국어", "과학", "사회"])
            with col2:
                grade = st.selectbox("학년", ["중1", "중2", "중3", "고1", "고2", "고3"])
                problem_type = st.selectbox("문제유형", ["객관식", "주관식", "서술형"])
            with col3:
                difficulty = st.selectbox("난이도", ["상", "중", "하"])
            
            problem_content = st.text_area("문제 내용", placeholder="문제 내용을 입력하세요.")
            
            # 객관식인 경우 보기 입력
            if problem_type == "객관식":
                st.subheader("보기 입력")
                col1, col2 = st.columns(2)
                with col1:
                    option1 = st.text_input("보기 1")
                    option3 = st.text_input("보기 3")
                    option5 = st.text_input("보기 5", "")
                with col2:
                    option2 = st.text_input("보기 2")
                    option4 = st.text_input("보기 4", "")
            else:
                option1 = option2 = option3 = option4 = option5 = ""
            
            answer = st.text_input("정답")
            keywords = st.text_input("키워드 (쉼표로 구분)")
            explanation = st.text_area("해설")
            
            submit_button = st.form_submit_button("문제 추가")
            
            if submit_button:
                if problem_id and subject and grade and problem_content and answer:
                    new_problem = [
                        problem_id, subject, grade, problem_type, difficulty, problem_content,
                        option1, option2, option3, option4, option5, answer, keywords, explanation
                    ]
                    
                    if SHEETS_AVAILABLE:
                        try:
                            # 마지막 행 다음에 추가
                            sheets_api.append_row('problems', new_problem)
                            st.success("문제가 Google Sheets에 성공적으로 추가되었습니다!")
                        except Exception as e:
                            st.error(f"문제 추가 중 오류가 발생했습니다: {str(e)}")
                    else:
                        try:
                            # CSV 파일에 추가
                            problems_df = pd.DataFrame([new_problem], columns=[
                                '문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                                '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설'
                            ])
                            problems_df.to_csv('new_problem.csv', mode='a', header=not os.path.exists('new_problem.csv'), index=False)
                            st.success("문제가 로컬 CSV 파일에 성공적으로 추가되었습니다!")
                        except Exception as e:
                            st.error(f"문제 추가 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.error("필수 필드(문제ID, 과목, 학년, 문제 내용, 정답)를 모두 입력해주세요.")
    
    with tab2:
        st.subheader("📈 성적 통계")
        
        if SHEETS_AVAILABLE:
            # 학생 답안 데이터 가져오기
            try:
                answers = sheets_api.get_student_answers()
                if answers:
                    answers_df = pd.DataFrame(answers)
                    
                    st.subheader("전체 제출 답안")
                    st.dataframe(answers_df)
                    
                    # 통계 정보
                    st.subheader("성적 통계")
                    avg_score = answers_df['점수'].astype(float).mean()
                    median_score = answers_df['점수'].astype(float).median()
                    max_score = answers_df['점수'].astype(float).max()
                    min_score = answers_df['점수'].astype(float).min()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("평균 점수", f"{avg_score:.1f}")
                    with col2:
                        st.metric("중간값", f"{median_score:.1f}")
                    with col3:
                        st.metric("최고 점수", f"{max_score:.1f}")
                    with col4:
                        st.metric("최저 점수", f"{min_score:.1f}")
                        
                    # 학생별 성적 차트
                    st.subheader("학생별 성적")
                    student_avg = answers_df.groupby(['학생ID', '이름'])['점수'].mean().reset_index()
                    st.bar_chart(student_avg.set_index('이름'))
                    
                    # 문제별 정답률
                    st.subheader("문제별 정답률")
                    problem_stats = answers_df.groupby('문제ID')['점수'].agg(['mean', 'count']).reset_index()
                    problem_stats.columns = ['문제ID', '평균 점수', '제출 수']
                    st.dataframe(problem_stats)
                    
                else:
                    st.info("아직 제출된 답안이 없습니다.")
            except Exception as e:
                st.error(f"성적 통계 로드 중 오류가 발생했습니다: {str(e)}")
        else:
            st.warning("Google Sheets API를 사용할 수 없어 성적 통계를 확인할 수 없습니다.")

def student_portal():
    st.title("👨‍🎓 학생 포털")
    
    # 학생 정보 입력
    if 'student_id' not in st.session_state:
        st.session_state.student_id = ""
        st.session_state.student_name = ""
        st.session_state.student_grade = ""
    
    if not st.session_state.student_id:
        with st.form("student_login"):
            st.subheader("로그인")
            student_id = st.text_input("학생 ID", placeholder="학번을 입력하세요")
            student_name = st.text_input("이름", placeholder="이름을 입력하세요")
            student_grade = st.selectbox("학년", ["", "중1", "중2", "중3", "고1", "고2", "고3"])
            
            submit = st.form_submit_button("로그인")
            
            if submit:
                if student_id and student_name and student_grade:
                    st.session_state.student_id = student_id
                    st.session_state.student_name = student_name
                    st.session_state.student_grade = student_grade
                    st.rerun()
                else:
                    st.error("모든 정보를 입력해주세요.")
    else:
        # 로그인된 상태
        st.write(f"안녕하세요, {st.session_state.student_name}님! ({st.session_state.student_grade})")
        
        if st.button("로그아웃", key="logout"):
            st.session_state.student_id = ""
            st.session_state.student_name = ""
            st.session_state.student_grade = ""
            st.rerun()
        
        # 문제 목록 표시
        st.subheader("📝 문제 목록")
        
        # 필터 옵션
        col1, col2, col3 = st.columns(3)
        with col1:
            subject_filter = st.selectbox("과목", ["전체", "영어", "수학", "국어", "과학", "사회"])
        with col2:
            grade_filter = st.selectbox("학년", ["전체", "중1", "중2", "중3", "고1", "고2", "고3"])
        with col3:
            difficulty_filter = st.selectbox("난이도", ["전체", "상", "중", "하"])
        
        if SHEETS_AVAILABLE:
            problems = sheets_api.get_problems()
        else:
            problems_df, _ = load_csv_data()
            problems = problems_df.to_dict('records') if problems_df is not None else []
        
        # 필터링
        filtered_problems = problems
        if subject_filter != "전체":
            filtered_problems = [p for p in filtered_problems if p['과목'] == subject_filter]
        if grade_filter != "전체":
            filtered_problems = [p for p in filtered_problems if p['학년'] == grade_filter]
        if difficulty_filter != "전체":
            filtered_problems = [p for p in filtered_problems if p['난이도'] == difficulty_filter]
        
        if filtered_problems:
            for problem in filtered_problems:
                with st.expander(f"{problem['문제ID']} - {problem['문제내용'][:30]}... ({problem['과목']}, {problem['학년']}, {problem['난이도']})"):
                    st.subheader(problem['문제내용'])
                    
                    # 객관식 문제 표시
                    if problem['문제유형'] == '객관식':
                        options = []
                        if problem['보기1']: options.append(problem['보기1'])
                        if problem['보기2']: options.append(problem['보기2'])
                        if problem['보기3']: options.append(problem['보기3'])
                        if problem['보기4']: options.append(problem['보기4'])
                        if problem['보기5']: options.append(problem['보기5'])
                        
                        user_answer = st.radio(
                            "답을 선택하세요:",
                            options,
                            key=f"radio_{problem['문제ID']}"
                        )
                    else:
                        # 주관식/서술형 문제
                        user_answer = st.text_area(
                            "답변을 입력하세요:",
                            key=f"text_{problem['문제ID']}"
                        )
                    
                    if st.button("제출", key=f"submit_{problem['문제ID']}"):
                        # 채점
                        score, feedback = grade_answer(
                            problem['문제유형'],
                            problem['정답'],
                            user_answer,
                            problem['키워드']
                        )
                        
                        # 결과 표시
                        st.markdown(f"""
                        <div class="result-card">
                            <h4>채점 결과</h4>
                            <p>점수: {score}/100</p>
                            <div class="feedback-box">
                                <p><strong>피드백:</strong> {feedback}</p>
                            </div>
                            <p><strong>해설:</strong> {problem['해설']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Google Sheets에 저장
                        if SHEETS_AVAILABLE:
                            try:
                                # 답안 저장
                                sheets_api.append_row('student_answers', [
                                    st.session_state.student_id,
                                    st.session_state.student_name,
                                    st.session_state.student_grade,
                                    problem['문제ID'],
                                    user_answer,
                                    score,
                                    feedback,
                                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                ])
                                st.success("답안이 제출되었습니다!")
                            except Exception as e:
                                st.error(f"답안 저장 중 오류가 발생했습니다: {str(e)}")
                        else:
                            # CSV 파일에 저장
                            try:
                                answer_data = {
                                    '학생ID': st.session_state.student_id,
                                    '이름': st.session_state.student_name,
                                    '학년': st.session_state.student_grade,
                                    '문제ID': problem['문제ID'],
                                    '제출답안': user_answer,
                                    '점수': score,
                                    '피드백': feedback,
                                    '제출시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                answer_df = pd.DataFrame([answer_data])
                                answer_df.to_csv('student_answers.csv', mode='a', header=not os.path.exists('student_answers.csv'), index=False)
                                st.success("답안이 로컬 CSV 파일에 저장되었습니다!")
                            except Exception as e:
                                st.error(f"답안 저장 중 오류가 발생했습니다: {str(e)}")
        else:
            st.info("조건에 맞는 문제가 없습니다.")

def login():
    st.title("🏫 학원 자동 첨삭 시스템")
    
    if st.session_state.authenticated:
        # 이미 인증됨
        # 사이드바 표시
        st.session_state.show_sidebar = True
        st.write("관리자로 로그인되었습니다.")
        
        # 교사 대시보드 표시
        teacher_dashboard()
        
        # 로그아웃 버튼
        if st.button("로그아웃"):
            st.session_state.authenticated = False
            st.session_state.show_sidebar = False
            st.rerun()
    else:
        # 인증 폼
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👨‍🏫 교사 로그인")
            with st.form("teacher_login"):
                teacher_id = st.text_input("교사 ID", placeholder="관리자 ID를 입력하세요")
                password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
                submit = st.form_submit_button("로그인")
                
                if submit:
                    # 간단한 인증 (실제로는 더 안전한 방법 사용)
                    if teacher_id == "admin" and password == "1234":
                        st.session_state.authenticated = True
                        st.session_state.show_sidebar = True
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 잘못되었습니다.")
        
        with col2:
            st.subheader("👨‍🎓 학생 포털")
            if st.button("학생 포털로 이동"):
                st.session_state.page = "student"
                st.rerun()

def main():
    # 페이지 상태 관리
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    
    # 페이지 라우팅
    if st.session_state.page == "login":
        login()
    elif st.session_state.page == "student":
        student_portal()
    
    # 홈으로 돌아가기 버튼
    if st.session_state.page != "login":
        if st.button("홈으로 돌아가기"):
            st.session_state.page = "login"
            st.rerun()

if __name__ == "__main__":
    main() 