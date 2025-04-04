import streamlit as st
import os
import pandas as pd
import base64
from datetime import datetime

# Google Sheets API 사용 여부 설정
USE_GOOGLE_SHEETS = False

# Google Sheets API가 사용 가능한 경우 모듈 임포트 시도
if USE_GOOGLE_SHEETS:
    try:
        from sheets.google_sheets import GoogleSheetsAPI
        sheets_api = GoogleSheetsAPI()
        SHEETS_AVAILABLE = True
    except ImportError:
        SHEETS_AVAILABLE = False
        st.error("Google Sheets API를 연결할 수 없습니다. 로컬 데이터를 사용합니다.")
else:
    SHEETS_AVAILABLE = False

# 초기 데이터 설정 (Google Sheets API 대신 메모리에 저장)
if 'problems' not in st.session_state:
    st.session_state.problems = [
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
        },
        {
            '문제ID': 'P003',
            '과목': '영어',
            '학년': '중2',
            '문제유형': '객관식',
            '난이도': '하',
            '문제내용': 'Which word is a verb?',
            '보기1': 'happy',
            '보기2': 'book',
            '보기3': 'run',
            '보기4': 'fast',
            '보기5': '',
            '정답': 'run',
            '키워드': 'verb,part of speech',
            '해설': '동사(verb)는 행동이나 상태를 나타내는 품사입니다. run(달리다)은 동사입니다.'
        }
    ]

if 'student_answers' not in st.session_state:
    st.session_state.student_answers = []

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'show_sidebar' not in st.session_state:
    st.session_state.show_sidebar = False

# Hide sidebar by default
st.set_page_config(initial_sidebar_state="collapsed")

def get_csv_download_link():
    """샘플 CSV 파일 다운로드 링크 생성"""
    with open('sample_problems.csv', 'r', encoding='utf-8') as f:
        csv = f.read()
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="sample_problems.csv">📥 샘플 CSV 파일 다운로드</a>'
    return href

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
</style>
""", unsafe_allow_html=True)

def teacher_dashboard():
    st.title("👨‍🏫 교사 대시보드")
    st.write("문제 관리 및 학생 성적 확인")
    
    tab1, tab2 = st.tabs(["문제 관리", "성적 통계"])
    
    with tab1:
        st.subheader("📝 문제 업로드")
        
        # CSV 가이드
        st.markdown("""
        <div class='csv-guide'>
        <h4>📋 CSV 파일 작성 가이드</h4>
        <p>다음 형식에 맞춰 CSV 파일을 작성해주세요:</p>
        <ul>
            <li>문제ID: 고유한 숫자</li>
            <li>과목: 수학, 영어, 국어 등</li>
            <li>학년: 중1, 중2, 중3, 고1, 고2, 고3</li>
            <li>문제유형: 객관식, 주관식, 서술형</li>
            <li>난이도: 상, 중, 하</li>
            <li>문제내용: 실제 문제 내용</li>
            <li>보기1~5: 객관식인 경우 보기 내용</li>
            <li>정답: 정답 또는 모범답안</li>
            <li>키워드: 채점 키워드(쉼표로 구분)</li>
            <li>해설: 문제 해설</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 샘플 CSV 다운로드 링크
        st.markdown("<div class='download-link'>", unsafe_allow_html=True)
        st.markdown(get_csv_download_link(), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 파일 업로드
        uploaded_file = st.file_uploader("CSV 파일 선택", type=['csv'])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success("파일이 성공적으로 업로드되었습니다!")
                
                # 업로드된 문제 미리보기
                st.subheader("📊 업로드된 문제 미리보기")
                st.dataframe(df)
                
                # 통계 정보
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("총 문제 수", len(df))
                with col2:
                    st.metric("문제 유형 수", len(df['문제유형'].unique()))
                with col3:
                    st.metric("과목 수", len(df['과목'].unique()))
                
            except Exception as e:
                st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
        
    with tab2:
        st.subheader("📈 성적 통계")
        st.write("학생들의 성적 통계를 확인할 수 있습니다.")

def student_portal():
    st.title("👨‍🎓 학생 포털")
    st.write("문제 풀기 및 성적 확인")
    
    tab1, tab2 = st.tabs(["문제 풀기", "성적 확인"])
    
    with tab1:
        st.subheader("문제 목록")
        st.write("풀고 싶은 문제를 선택하세요.")
        
    with tab2:
        st.subheader("나의 성적")
        st.write("제출한 문제의 성적을 확인할 수 있습니다.")

def login():
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>📚 학원 자동 첨삭 시스템</h1>", unsafe_allow_html=True)
    
    # Create columns for centering the login form
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 2rem; border-radius: 10px;'>
            <h2 style='text-align: center; margin-bottom: 2rem;'>로그인</h2>
        """, unsafe_allow_html=True)
        
        username = st.text_input("아이디", key="username")
        password = st.text_input("비밀번호", type="password", key="password")
        
        # Show demo credentials with toggle
        with st.expander("데모 계정 정보 보기"):
            st.markdown("""
            **교사 계정**
            - 아이디: teacher
            - 비밀번호: demo1234
            
            **학생 계정**
            - 아이디: student
            - 비밀번호: demo5678
            """)
        
        if st.button("로그인"):
            if (username == "teacher" and password == "demo1234") or \
               (username == "student" and password == "demo5678"):
                st.session_state.authenticated = True
                st.session_state.user_type = "teacher" if username == "teacher" else "student"
                st.session_state.show_sidebar = True
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")
        
        st.markdown("</div>", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ''
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ''
    if 'grade' not in st.session_state:
        st.session_state.grade = ''

def show_problems():
    """Display available problems"""
    st.title(f'📚 {st.session_state.user_name}님의 문제 풀이')
    
    if not SHEETS_AVAILABLE:
        st.info('Google Sheets API를 사용할 수 없습니다.')
        return
    
    problems = st.session_state.problems
    
    if not problems:
        st.info('현재 등록된 문제가 없습니다.')
        return
    
    for problem in problems:
        if len(problem) >= 6:  # Ensure problem has required fields
            with st.expander(f"문제 {problem['문제ID']}: {problem['문제내용'][:50]}..."):
                st.write(f"**과목:** {problem['과목']}")
                st.write(f"**학년:** {problem['학년']}")
                st.write(f"**유형:** {problem['문제유형']}")
                st.write(f"**난이도:** {problem['난이도']}")
                st.write(f"**문제 내용:**\n{problem['문제내용']}")
                
                # Display options if they exist
                for i in range(1, 6):
                    if i < len(problem) and problem[f'보기{i}']:
                        st.write(f"**보기 {i}:** {problem[f'보기{i}']}")
                
                # Answer submission
                with st.form(f"answer_form_{problem['문제ID']}"):
                    answer = st.text_area("답안 작성")
                    if st.form_submit_button("제출"):
                        submit_answer(problem['문제ID'], answer)

def submit_answer(problem_id, answer):
    """Submit student's answer"""
    if not answer:
        st.error("답안을 입력해주세요.")
        return
    
    submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare answer data
    answer_data = [
        st.session_state.user_id,
        st.session_state.user_name,
        st.session_state.grade,
        problem_id,
        answer,
        "",  # Score (to be filled by teacher)
        "",  # Feedback (to be filled by teacher)
        submission_time
    ]
    
    # Submit to Google Sheets
    st.session_state.student_answers.append(answer_data)
    st.success("답안이 성공적으로 제출되었습니다!")

def main():
    """Main application function"""
    init_session_state()
    
    if not st.session_state.authenticated:
        login()
    else:
        # Show sidebar only after authentication
        if st.session_state.show_sidebar:
            st.sidebar.title("메뉴")
            
            # Available pages based on user type
            if st.session_state.user_type == "teacher":
                page = st.sidebar.radio(
                    "페이지 선택",
                    ["교사 대시보드"]
                )
                teacher_dashboard()
            else:
                student_portal()
            
            if st.sidebar.button("로그아웃"):
                st.session_state.authenticated = False
                st.session_state.show_sidebar = False
                st.rerun()
        else:
            show_problems()

if __name__ == "__main__":
    main() 