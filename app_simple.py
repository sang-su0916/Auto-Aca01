import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# 페이지 설정 - 반드시 첫 번째 Streamlit 명령어여야 함
st.set_page_config(
    page_title="학원 자동 첨삭 시스템",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"  # 사이드바를 기본적으로 숨김
)

# Google Sheets 연동 관련 import 시도
try:
    from sheets.setup_sheets import fetch_problems_from_sheet, SPREADSHEET_ID
    SHEETS_AVAILABLE = True
except ImportError as e:
    SHEETS_AVAILABLE = False
    st.error(f"Google Sheets 연동 모듈을 가져오는 중 오류 발생: {str(e)}")
    # 기본 스프레드시트 ID 설정
    SPREADSHEET_ID = "1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0"

# 사용자 계정 정보
def initialize_user_db():
    # Streamlit Cloud에서 사용할 기본 사용자 데이터
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
        },
        "student3": {
            "password": "1234",
            "name": "박영희",
            "role": "student",
            "grade": "중1"
        }
    }
    return default_users

# 사용자 데이터베이스 로드
users_db = initialize_user_db()

# 기본 데이터 초기화
def initialize_sample_questions():
    if SHEETS_AVAILABLE:
        try:
            # Google Sheets에서 문제 데이터 가져오기
            df = fetch_problems_from_sheet()
            if not df.empty:
                st.success(f"Google Sheets에서 {len(df)}개의 문제를 가져왔습니다.")
                return df
            else:
                st.warning("Google Sheets에서 문제를 가져오지 못했습니다. 기본 문제를 생성합니다.")
        except Exception as e:
            st.error(f"Google Sheets 연결 오류: {str(e)}")
            st.error("기본 문제를 생성합니다.")
    else:
        st.warning("Google Sheets 연동 모듈을 사용할 수 없습니다. 기본 문제를 생성합니다.")
    
    # 기본 문제 생성 (Sheets 연결 실패 시)
    questions = []
    
    # 학년별로 각 20문제씩 생성
    grades = ["중1", "중2", "중3"]
    
    for grade_idx, grade in enumerate(grades):
        for i in range(1, 21):
            idx = grade_idx * 20 + i
            questions.append({
                '문제ID': f'P{idx:03d}',
                '과목': '영어',
                '학년': grade,
                '문제유형': '객관식' if i % 3 != 0 else '주관식',
                '난이도': '중' if i % 3 == 0 else ('상' if i % 3 == 1 else '하'),
                '문제내용': f'{grade} 영어 문제 {i}: {get_question_by_grade(grade, i)}',
                '보기1': get_option_by_grade(grade, i, 1),
                '보기2': get_option_by_grade(grade, i, 2),
                '보기3': get_option_by_grade(grade, i, 3),
                '보기4': get_option_by_grade(grade, i, 4),
                '보기5': get_option_by_grade(grade, i, 5),
                '정답': get_answer_by_grade(grade, i),
                '키워드': get_keywords_by_grade(grade),
                '해설': f'정답은 {get_answer_by_grade(grade, i)}입니다.'
            })
    
    return pd.DataFrame(questions)

def get_question_by_grade(grade, i):
    if grade == "중1":
        return "Which of the following is a fruit?"
    elif grade == "중2":
        return "What time is it?"
    elif grade == "중3":
        return "Which word is a verb?"
    return "Sample question"

def get_option_by_grade(grade, i, option_num):
    if grade == "중1":
        options = [['Apple', 'Car', 'Book', 'Pen', ''],
                  ['Banana', 'House', 'Computer', 'Pencil', ''],
                  ['Orange', 'School', 'Desk', 'Eraser', ''],
                  ['Strawberry', 'Door', 'Chair', 'Ruler', ''],
                  ['Grape', 'Window', 'Table', 'Bag', '']]
        return options[i % 5][option_num-1]
    elif grade == "중2":
        options = [['2:30', '3:15', '4:00', '5:45', ''],
                  ['4:45', '1:00', '6:30', '8:20', ''],
                  ['7:20', '9:10', '10:00', '11:30', ''],
                  ['10:55', '12:05', '1:15', '2:40', ''],
                  ['6:40', '7:50', '9:25', '11:10', '']]
        return options[i % 5][option_num-1]
    elif grade == "중3":
        # 동사 문제에 대한 보기 개선 - 각 세트는 하나의 동사와 여러 개의 명사, 형용사 등으로 구성
        options = [
            ['Run', 'Book', 'School', 'Red', ''],
            ['Write', 'Table', 'Beautiful', 'Computer', ''],
            ['Speak', 'Pen', 'Happy', 'Chair', ''],
            ['Play', 'House', 'Sad', 'Window', ''],
            ['Study', 'Phone', 'Angry', 'Notebook', '']
        ]
        return options[i % 5][option_num-1]
    return ""

def get_answer_by_grade(grade, i):
    if grade == "중1":
        return ['Apple', 'Banana', 'Orange', 'Strawberry', 'Grape'][i % 5]
    elif grade == "중2":
        return ['2:30', '4:45', '7:20', '10:55', '6:40'][i % 5]
    elif grade == "중3":
        # 동사 문제의 정답은 항상 첫 번째 옵션 (동사)
        return ['Run', 'Write', 'Speak', 'Play', 'Study'][i % 5]
    return "Answer"

def get_keywords_by_grade(grade):
    if grade == "중1":
        return "fruit,food"
    elif grade == "중2":
        return "time,clock,hour"
    elif grade == "중3":
        return "verb,action"
    return "keywords"

def initialize_student_answers():
    return pd.DataFrame(columns=[
        '학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간'
    ])

# 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "login"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "username": "",
        "name": "",
        "role": "",
        "grade": ""
    }
if "problems_df" not in st.session_state:
    st.session_state.problems_df = initialize_sample_questions()
if "answers_df" not in st.session_state:
    st.session_state.answers_df = initialize_student_answers()
if "current_problem_index" not in st.session_state:
    st.session_state.current_problem_index = 0
if "total_problems" not in st.session_state:
    st.session_state.total_problems = 20

# 스타일 설정
st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 상단 네비게이션 */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background-color: #f8f9fa;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    .nav-logo {
        font-weight: bold;
        font-size: 1.2rem;
        display: flex;
        align-items: center;
    }
    .nav-logo img {
        height: 30px;
        margin-right: 10px;
    }
    .nav-menu {
        display: flex;
        gap: 20px;
    }
    .nav-user {
        font-size: 0.9rem;
        color: #555;
    }
    .nav-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9rem;
    }
    .nav-button:hover {
        background-color: #45a049;
    }
    
    /* 문제지 스타일 */
    .exam-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .result-card {
        background-color: #f1f8e9;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #4CAF50;
    }
    .feedback-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #2196F3;
    }
    .problem-card {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .problem-number {
        font-weight: bold;
        color: #1976D2;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    .problem-content {
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    .options-container {
        margin-left: 1rem;
    }
    .answer-section {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
    }
    .correct-answer {
        background-color: #E8F5E9;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin-top: 0.5rem;
        border-left: 4px solid #4CAF50;
    }
    .wrong-answer {
        background-color: #FFEBEE;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin-top: 0.5rem;
        border-left: 4px solid #F44336;
    }
    .exam-title {
        text-align: center;
        font-weight: bold;
        font-size: 1.6rem;
        margin-bottom: 2.5rem;
        padding: 1rem;
        background-color: #f0f0f0;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .student-info {
        margin-bottom: 1.5rem;
        padding: 0.8rem;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        font-size: 1rem;
        background-color: #fafafa;
    }
    .login-container {
        max-width: 450px;
        margin: 3rem auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .login-logo {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-title {
        font-size: 1.8rem;
        text-align: center;
        margin-bottom: 1.5rem;
        color: #333;
    }
    .stats-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .stats-number {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1976D2;
    }
    .stats-label {
        font-size: 0.9rem;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# 채점 함수
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
        
        return 0, f"오답입니다. 정답은 '{correct_answer}'입니다."
    
    return 0, "알 수 없는 문제 유형입니다."

# 사용자 인증 함수
def authenticate_user(username, password):
    if username in users_db and users_db[username]['password'] == password:
        user_data = users_db[username]
        st.session_state.authenticated = True
        st.session_state.user_data = {
            "username": username,
            "name": user_data["name"],
            "role": user_data["role"],
            "grade": user_data["grade"]
        }
        
        # 학생인 경우 학생 페이지로, 교사인 경우 교사 페이지로
        if user_data["role"] == "student":
            st.session_state.page = "student"
            
            # 학생 로그인 시 문제 인덱스 초기화
            st.session_state.current_problem_index = 0
        else:
            st.session_state.page = "teacher"
        
        return True
    return False

# 로그아웃 함수
def logout():
    st.session_state.authenticated = False
    st.session_state.user_data = {
        "username": "",
        "name": "",
        "role": "",
        "grade": ""
    }
    st.session_state.page = "login"

# 다음 문제로 이동
def next_problem():
    if st.session_state.current_problem_index < st.session_state.total_problems - 1:
        st.session_state.current_problem_index += 1

# 이전 문제로 이동
def prev_problem():
    if st.session_state.current_problem_index > 0:
        st.session_state.current_problem_index -= 1

# 상단 네비게이션 바 컴포넌트
def render_navbar():
    if st.session_state.authenticated:
        # f-string 대신 일반 문자열과 format 사용
        role_menu = '<a href="javascript:void(0);" onclick="parent.streamlitClick(\'teacher\')">문제 관리</a>' if st.session_state.user_data["role"] == "teacher" else '<a href="javascript:void(0);" onclick="parent.streamlitClick(\'student\')">문제 풀기</a>'
        stats_menu = '<a href="javascript:void(0);" onclick="parent.streamlitClick(\'stats\')">성적 통계</a>' if st.session_state.user_data["role"] == "teacher" else '<a href="javascript:void(0);" onclick="parent.streamlitClick(\'grades\')">내 성적</a>'
        user_role = '선생님' if st.session_state.user_data['role'] == 'teacher' else '학생'
        
        # JSON 객체를 위한 JavaScript 코드 부분 - 중괄호를 포맷팅에서 분리
        js_script = """
        <script>
            function streamlitClick(action) {
                const data = {"action": action};
                window.parent.postMessage({"type": "streamlit:setComponentValue", "value": data}, "*");
            }
        </script>
        """
        
        html = """
        <div class="nav-container">
            <div class="nav-logo">
                <img src="https://cdn-icons-png.flaticon.com/128/2436/2436882.png" alt="Logo"> 학원 자동 첨삭 시스템
            </div>
            <div class="nav-menu">
                {role_menu}
                {stats_menu}
            </div>
            <div class="nav-user">
                {user_name} ({user_role})
                <button class="nav-button" onclick="parent.streamlitClick('logout')">로그아웃</button>
            </div>
        </div>
        {js_script}
        """.format(
            role_menu=role_menu,
            stats_menu=stats_menu,
            user_name=st.session_state.user_data['name'],
            user_role=user_role,
            js_script=js_script
        )
        st.markdown(html, unsafe_allow_html=True)
        
        # JavaScript 이벤트 처리
        nav_action = st.text_input("", "", key="nav_action", label_visibility="collapsed")
        if nav_action:
            try:
                action_data = json.loads(nav_action)
                if action_data.get('action') == 'logout':
                    logout()
                    st.rerun()
                elif action_data.get('action') == 'teacher':
                    st.session_state.page = "teacher"
                    st.rerun()
                elif action_data.get('action') == 'student':
                    st.session_state.page = "student"
                    st.rerun()
                elif action_data.get('action') == 'stats':
                    st.session_state.page = "teacher"
                    st.rerun()
                elif action_data.get('action') == 'grades':
                    st.session_state.page = "student"
                    st.session_state.student_tab = "grades"
                    st.rerun()
            except json.JSONDecodeError:
                st.error("잘못된 형식의 JSON 데이터입니다.")
                print(f"JSON 파싱 에러: {nav_action}")

# 학생 포털
def student_portal():
    # 상단 네비게이션 바
    render_navbar()
    
    # 학생 탭 상태 초기화
    if "student_tab" not in st.session_state:
        st.session_state.student_tab = "problems"
    
    # 제출 답안 추적을 위한 상태 초기화
    if "submitted_answers" not in st.session_state:
        st.session_state.submitted_answers = {}
    
    # 탭 설정: 문제 풀기, 내 성적
    tab1, tab2 = st.tabs(["📝 문제 풀기", "📊 내 성적"])
    
    # 탭 선택
    if st.session_state.student_tab == "grades":
        tab2.selectbox = True
    
    with tab1: # 문제 풀기 탭
        st.markdown("""<div class="exam-container">""", unsafe_allow_html=True)
        
        # 시험지 제목
        st.markdown(f"""
        <div class='exam-title'>
            🏫 {st.session_state.user_data['grade']} 영어 시험
        </div>
        """, unsafe_allow_html=True)
        
        # 학생 정보 표시
        st.markdown(f"""
        <div class='student-info'>
            <strong>이름:</strong> {st.session_state.user_data['name']} | 
            <strong>학년:</strong> {st.session_state.user_data['grade']} | 
            <strong>학생ID:</strong> {st.session_state.user_data['username']}
        </div>
        """, unsafe_allow_html=True)
        
        # 문제 필터링 (학생 학년에 맞는 문제)
        filtered_problems = st.session_state.problems_df[
            st.session_state.problems_df['학년'] == st.session_state.user_data['grade']
        ]
        
        if len(filtered_problems) == 0:
            st.warning(f"{st.session_state.user_data['grade']} 학년에 해당하는 문제가 없습니다. 관리자에게 문의하세요.")
        else:
            # 학생 답안 기록 가져오기
            student_answers = st.session_state.answers_df[
                st.session_state.answers_df['학생ID'] == st.session_state.user_data['username']
            ]
            
            # 학생이 이미 제출한 문제 ID 세트 생성
            submitted_problem_ids = set(student_answers['문제ID'].values)
            
            # 문제 목록
            for i, (_, problem) in enumerate(filtered_problems.iterrows()):
                problem_id = problem['문제ID']
                already_submitted = problem_id in submitted_problem_ids
                
                # 이미 제출한 문제의 답안과 채점 결과 찾기
                if already_submitted:
                    submitted_answer = student_answers[student_answers['문제ID'] == problem_id].iloc[0]
                    user_answer = submitted_answer['제출답안']
                    score = submitted_answer['점수']
                    feedback = submitted_answer['피드백']
                
                with st.container():
                    st.markdown(f"""
                    <div class='problem-card'>
                        <div class='problem-number'>문제 {i+1}. [{problem['난이도']}] - {problem['문제유형']}</div>
                        <div class='problem-content'>{problem['문제내용']}</div>
                    """, unsafe_allow_html=True)
                    
                    # 객관식 문제
                    if problem['문제유형'] == '객관식':
                        options = []
                        for j in range(1, 6):
                            if problem[f'보기{j}'] and not pd.isna(problem[f'보기{j}']):
                                options.append(problem[f'보기{j}'])
                        
                        # 이미 제출한 문제면 선택된 답안 표시하고 disabled 설정
                        if already_submitted:
                            # 선택된 답안의 인덱스 찾기
                            try:
                                selected_idx = options.index(user_answer)
                            except ValueError:
                                selected_idx = 0  # 기본값 (찾지 못한 경우)
                            
                            answer = st.radio(
                                "답을 선택하세요:",
                                options,
                                index=selected_idx,
                                key=f"answer_{problem_id}",
                                disabled=True
                            )
                            
                            # 채점 결과 표시
                            if score == 100:
                                st.markdown(f"""
                                <div class='correct-answer'>
                                    <strong>✅ 정답입니다!</strong><br>
                                    정답: {problem['정답']}<br>
                                    해설: {problem['해설']}
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class='wrong-answer'>
                                    <strong>❌ {feedback}</strong><br>
                                    정답: {problem['정답']}<br>
                                    해설: {problem['해설']}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            # 아직 제출하지 않은 문제는 일반적으로 표시
                            answer = st.radio(
                                "답을 선택하세요:",
                                options,
                                key=f"answer_{problem_id}",
                                index=None  # 기본 선택 없음
                            )
                            
                            col1, col2, col3 = st.columns([6, 4, 2])
                            with col3:
                                if st.button("제출", key=f"submit_{problem_id}"):
                                    if answer:  # 답을 선택했는지 확인
                                        # 채점
                                        score, feedback = grade_answer(
                                            problem['문제유형'], 
                                            problem['정답'], 
                                            answer,
                                            problem.get('키워드', '')
                                        )
                                        
                                        # 답안 기록
                                        _record_answer(
                                            problem_id,
                                            answer,
                                            score,
                                            feedback
                                        )
                                        
                                        # 채점 결과 표시
                                        if score == 100:
                                            st.markdown(f"""
                                            <div class='correct-answer'>
                                                <strong>✅ 정답입니다!</strong><br>
                                                정답: {problem['정답']}<br>
                                                해설: {problem['해설']}
                                            </div>
                                            """, unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"""
                                            <div class='wrong-answer'>
                                                <strong>❌ {feedback}</strong><br>
                                                정답: {problem['정답']}<br>
                                                해설: {problem['해설']}
                                            </div>
                                            """, unsafe_allow_html=True)
                                        
                                        # 페이지 새로고침하여 제출 상태 업데이트
                                        st.rerun()
                                    else:
                                        st.error("답을 선택해주세요.")
                    
                    # 주관식 문제
                    else:
                        # 이미 제출한 문제면 답안 표시하고 disabled 설정
                        if already_submitted:
                            answer = st.text_area(
                                "답을 입력하세요:", 
                                value=user_answer,
                                key=f"answer_{problem_id}",
                                disabled=True
                            )
                            
                            # 채점 결과 표시
                            if score == 100:
                                st.markdown(f"""
                                <div class='correct-answer'>
                                    <strong>✅ 정답입니다!</strong><br>
                                    정답: {problem['정답']}<br>
                                    해설: {problem['해설']}
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class='wrong-answer'>
                                    <strong>❌ {feedback}</strong><br>
                                    정답: {problem['정답']}<br>
                                    해설: {problem['해설']}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            # 아직 제출하지 않은 문제는 일반적으로 표시
                            answer = st.text_area("답을 입력하세요:", key=f"answer_{problem_id}")
                            
                            col1, col2, col3 = st.columns([6, 4, 2])
                            with col3:
                                if st.button("제출", key=f"submit_{problem_id}"):
                                    if answer.strip():  # 답을 입력했는지 확인
                                        # 채점
                                        score, feedback = grade_answer(
                                            problem['문제유형'], 
                                            problem['정답'], 
                                            answer,
                                            problem.get('키워드', '')
                                        )
                                        
                                        # 답안 기록
                                        _record_answer(
                                            problem_id,
                                            answer,
                                            score,
                                            feedback
                                        )
                                        
                                        # 채점 결과 표시
                                        if score == 100:
                                            st.markdown(f"""
                                            <div class='correct-answer'>
                                                <strong>✅ 정답입니다!</strong><br>
                                                정답: {problem['정답']}<br>
                                                해설: {problem['해설']}
                                            </div>
                                            """, unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"""
                                            <div class='wrong-answer'>
                                                <strong>❌ {feedback}</strong><br>
                                                정답: {problem['정답']}<br>
                                                해설: {problem['해설']}
                                            </div>
                                            """, unsafe_allow_html=True)
                                        
                                        # 페이지 새로고침하여 제출 상태 업데이트
                                        st.rerun()
                                    else:
                                        st.error("답을 입력해주세요.")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2: # 내 성적 탭
        st.markdown("""<div class="exam-container">""", unsafe_allow_html=True)
        st.markdown("<h2>내 성적</h2>", unsafe_allow_html=True)
        
        # 학생 정보 표시
        st.markdown(f"""
        <div class='student-info'>
            <strong>이름:</strong> {st.session_state.user_data['name']} | 
            <strong>학년:</strong> {st.session_state.user_data['grade']} | 
            <strong>학생ID:</strong> {st.session_state.user_data['username']}
        </div>
        """, unsafe_allow_html=True)
        
        # 학생의 답안 기록 필터링
        student_answers = st.session_state.answers_df[
            st.session_state.answers_df['학생ID'] == st.session_state.user_data['username']
        ]
        
        if len(student_answers) == 0:
            st.info("아직 풀이한 문제가 없습니다. 문제를 풀어보세요!")
        else:
            # 성적 요약
            avg_score = student_answers['점수'].mean()
            answered_count = len(student_answers)
            correct_count = len(student_answers[student_answers['점수'] == 100])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div class="stats-card">
                    <div class="stats-number">{}</div>
                    <div class="stats-label">푼 문제 수</div>
                </div>
                """.format(answered_count), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="stats-card">
                    <div class="stats-number">{}</div>
                    <div class="stats-label">맞은 문제 수</div>
                </div>
                """.format(correct_count), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="stats-card">
                    <div class="stats-number">{:.1f}</div>
                    <div class="stats-label">평균 점수</div>
                </div>
                """.format(avg_score), unsafe_allow_html=True)
            
            # 답안 기록 표
            st.markdown("<h3>답안 기록</h3>", unsafe_allow_html=True)
            
            for _, answer in student_answers.iterrows():
                problem_id = answer['문제ID']
                problem = st.session_state.problems_df[st.session_state.problems_df['문제ID'] == problem_id].iloc[0]
                
                with st.expander(f"{problem['문제내용']} - {answer['제출시간']}"):
                    st.markdown(f"**제출 답안:** {answer['제출답안']}")
                    st.markdown(f"**정답:** {problem['정답']}")
                    st.markdown(f"**점수:** {answer['점수']}")
                    st.markdown(f"**피드백:** {answer['피드백']}")
        
        st.markdown("</div>", unsafe_allow_html=True)

# 교사 대시보드
def teacher_dashboard():
    # 상단 네비게이션 바
    render_navbar()
    
    # 탭 설정
    tab1, tab2 = st.tabs(["📝 문제 관리", "📊 성적 통계"])
    
    with tab1:
        st.markdown("""<div class="exam-container">""", unsafe_allow_html=True)
        st.markdown("<h2>문제 관리</h2>", unsafe_allow_html=True)
        
        # Google Sheets 연동 상태 표시
        if SHEETS_AVAILABLE:
            st.success("Google Sheets 연동이 활성화되어 있습니다.")
            # Google Sheets ID는 개발자만 볼 수 있도록 토글로 숨김
            with st.expander("Google Sheets 연동 정보", expanded=False):
                st.info(f"Google Sheets ID: {SPREADSHEET_ID}")
        else:
            st.warning("Google Sheets 연동이 비활성화되어 있습니다. 기본 문제가 사용됩니다.")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            # 새로고침 버튼
            if st.button("문제 새로고침"):
                st.session_state.problems_df = initialize_sample_questions()
                st.success("문제가 새로고침되었습니다!")
                st.rerun()
        
        # 기존 문제 표시
        problems_df = st.session_state.problems_df
        
        # 학년별 필터링
        grade_filter = st.selectbox("학년별 필터링", ["전체"] + sorted(problems_df['학년'].unique().tolist()))
        
        if grade_filter != "전체":
            filtered_df = problems_df[problems_df['학년'] == grade_filter]
        else:
            filtered_df = problems_df
        
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
            st.success(f"총 {len(filtered_df)}개의 문제가 등록되어 있습니다.")
        else:
            st.info("현재 등록된 문제가 없습니다.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 성적 통계 탭
    with tab2:
        st.markdown("""<div class="exam-container">""", unsafe_allow_html=True)
        st.markdown("<h2>성적 통계</h2>", unsafe_allow_html=True)
        
        # 학생 답안 데이터 로드
        student_answers_df = st.session_state.answers_df
        
        if not student_answers_df.empty:
            # 학년별 필터링
            st.markdown("<h3>학생별 점수</h3>", unsafe_allow_html=True)
            
            st.dataframe(student_answers_df, use_container_width=True)
            
            # 간단한 통계
            if '점수' in student_answers_df.columns:
                # 학생별 평균 점수
                student_avg = student_answers_df.groupby('이름')['점수'].mean().reset_index()
                student_avg.columns = ['학생', '평균 점수']
                
                st.markdown("<h3>학생별 평균 점수</h3>", unsafe_allow_html=True)
                st.dataframe(student_avg, use_container_width=True)
                
                # 학년별 평균 점수
                grade_avg = student_answers_df.groupby('학년')['점수'].mean().reset_index()
                grade_avg.columns = ['학년', '평균 점수']
                
                st.markdown("<h3>학년별 평균 점수</h3>", unsafe_allow_html=True)
                st.dataframe(grade_avg, use_container_width=True)
        else:
            st.info("아직 제출된 학생 답안이 없습니다.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# 답안 기록 함수
def _record_answer(problem_id, answer, score, feedback):
    new_answer = {
        '학생ID': st.session_state.user_data['username'],
        '이름': st.session_state.user_data['name'],
        '학년': st.session_state.user_data['grade'],
        '문제ID': problem_id,
        '제출답안': answer,
        '점수': score,
        '피드백': feedback,
        '제출시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 답안 DataFrame에 추가
    st.session_state.answers_df = pd.concat([
        st.session_state.answers_df, 
        pd.DataFrame([new_answer])
    ], ignore_index=True)
                

# 로그인 화면
def login():
    st.markdown("""
    <div class="login-container">
        <div class="login-logo">
            <img src="https://cdn-icons-png.flaticon.com/128/2436/2436882.png" alt="Logo" width="80">
        </div>
        <h1 class="login-title">학원 자동 첨삭 시스템</h1>
    """, unsafe_allow_html=True)
    
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    
    if st.button("로그인", key="login_btn"):
        if authenticate_user(username, password):
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
    
    # 기본 계정 정보는 화면에 표시하지 않음
    # 기본 계정 정보를 표시할 수 있는 버튼 추가
    if st.checkbox("기본 계정 정보 보기", value=False):
        st.markdown("---")
        st.markdown("### 기본 계정")
        st.markdown("- 교사: `admin` / `1234` (관리자, 선생님)")
        st.markdown("- 학생1: `student1` / `1234` (홍길동, 중3)")
        st.markdown("- 학생2: `student2` / `1234` (김철수, 중2)")
        st.markdown("- 학생3: `student3` / `1234` (박영희, 중1)")
    
    st.markdown("</div>", unsafe_allow_html=True)

# 메인 앱 실행
def main():
    # 페이지 라우팅
    if not st.session_state.authenticated:
        login()
    else:
        if st.session_state.user_data["role"] == "teacher":
            teacher_dashboard()
        else:
            student_portal()

if __name__ == "__main__":
    main()
