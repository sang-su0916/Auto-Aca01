import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="학원 자동 첨삭 시스템",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Google 스프레드시트 ID 설정 - 참고용으로만 표시
SPREADSHEET_ID = "1YcKaHcjnx5-WypEpYbcfg04s8TIq280l-gi6iISF5NQ"

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

# 구글 시트 API 연결 함수
def get_problems_from_google_sheets():
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        # 인증 파일 확인
        if not os.path.exists('credentials.json'):
            return None
        
        # 서비스 계정 인증
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        
        # 시트에서 문제 데이터 가져오기
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='problems!A2:N'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return None
            
        # 데이터프레임 생성
        columns = ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                  '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
        
        data = []
        for row in values:
            # 모든 열을 확보
            row_extended = row + [''] * (len(columns) - len(row))
            row_dict = {columns[i]: row_extended[i] for i in range(len(columns))}
            data.append(row_dict)
            
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"구글 시트에서 문제 가져오기 오류: {str(e)}")
        return None

# 기본 데이터 초기화 수정
def initialize_sample_questions():
    # 먼저 구글 시트에서 문제 가져오기 시도
    google_sheets_data = get_problems_from_google_sheets()
    if google_sheets_data is not None and not google_sheets_data.empty:
        return google_sheets_data
    
    # 구글 시트에서 가져오기 실패시 기본 데이터 사용
    questions = []
    
    # 중1 영어 문제 - 과일
    for i in range(1, 8):
        questions.append({
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중1',
            '문제유형': '객관식',
            '난이도': ['상', '중', '하'][i % 3],
            '문제내용': f'다음 중 과일이 아닌 것은?',
            '보기1': '사과 (Apple)',
            '보기2': '바나나 (Banana)',
            '보기3': '당근 (Carrot)',
            '보기4': '오렌지 (Orange)',
            '보기5': '',
            '정답': '당근 (Carrot)',
            '키워드': 'fruit,vegetable',
            '해설': '당근(Carrot)은 채소(vegetable)입니다. 나머지는 모두 과일(fruit)입니다.'
        })
    
    # 중1 영어 문제 - 색상
    for i in range(8, 15):
        questions.append({
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중1',
            '문제유형': '객관식',
            '난이도': ['상', '중', '하'][i % 3],
            '문제내용': f'다음 중 빨간색을 의미하는 영어 단어는?',
            '보기1': 'Blue',
            '보기2': 'Red',
            '보기3': 'Green',
            '보기4': 'Yellow',
            '보기5': '',
            '정답': 'Red',
            '키워드': 'color,red',
            '해설': 'Red는 빨간색, Blue는 파란색, Green은 녹색, Yellow는 노란색입니다.'
        })
    
    # 중2 영어 문제 - 시간
    for i in range(15, 22):
        questions.append({
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중2',
            '문제유형': '주관식',
            '난이도': ['중', '하', '상'][i % 3],
            '문제내용': f'영어로 "지금 3시 30분이다"를 올바르게 표현한 것은?',
            '보기1': '',
            '보기2': '',
            '보기3': '',
            '보기4': '',
            '보기5': '',
            '정답': 'It is three thirty.',
            '키워드': 'time,clock,three,thirty',
            '해설': '시간 표현에서는 "It is + 시간"의 형태로 표현합니다. 3:30은 "three thirty"라고 표현합니다.'
        })
    
    # 중2 영어 문제 - 방향
    for i in range(22, 29):
        questions.append({
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중2',
            '문제유형': '객관식',
            '난이도': ['중', '상', '하'][i % 3],
            '문제내용': f'다음 중 "남쪽"을 의미하는 영어 단어는?',
            '보기1': 'North',
            '보기2': 'East',
            '보기3': 'West',
            '보기4': 'South',
            '보기5': '',
            '정답': 'South',
            '키워드': 'direction,south',
            '해설': 'South는 남쪽, North는 북쪽, East는 동쪽, West는 서쪽을 의미합니다.'
        })
    
    # 중3 영어 문제 - 동사
    for i in range(29, 36):
        questions.append({
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중3',
            '문제유형': '객관식',
            '난이도': ['상', '중', '하'][i % 3],
            '문제내용': f'다음 중 동사(verb)가 아닌 것은?',
            '보기1': 'Run',
            '보기2': 'Book',
            '보기3': 'Jump',
            '보기4': 'Swim',
            '보기5': '',
            '정답': 'Book',
            '키워드': 'verb,noun',
            '해설': 'Book은 명사(책)입니다. Run(달리다), Jump(뛰다), Swim(수영하다)은 모두 동사입니다.'
        })
    
    # 중3 영어 문제 - 문법
    for i in range(36, 43):
        questions.append({
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중3',
            '문제유형': '주관식',
            '난이도': ['하', '상', '중'][i % 3],
            '문제내용': f'다음 문장의 빈칸에 알맞은 관사를 넣으세요: "I saw ___ elephant at the zoo."',
            '보기1': '',
            '보기2': '',
            '보기3': '',
            '보기4': '',
            '보기5': '',
            '정답': 'an',
            '키워드': 'article,an,vowel',
            '해설': '모음(a, e, i, o, u)으로 시작하는 단어 앞에는 부정관사 "an"을 사용합니다. Elephant는 "e"로 시작하므로 "an"을 사용합니다.'
        })
    
    return pd.DataFrame(questions)

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

# 스타일 설정
st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
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
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .nav-button {
        margin-top: 10px;
    }
    .connection-warning {
        background-color: #FFFCE9;
        padding: 8px 16px;
        border-radius: 8px;
        border-left: 4px solid #FFEB3B;
        margin-bottom: 16px;
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
    problems_df = st.session_state.problems_df
    student_grade = st.session_state.user_data['grade']
    filtered_problems = problems_df[problems_df['학년'] == student_grade]
    
    if st.session_state.current_problem_index < len(filtered_problems) - 1:
        st.session_state.current_problem_index += 1
    else:
        # 마지막 문제인 경우 처음으로 돌아감
        st.session_state.current_problem_index = 0

# 이전 문제로 이동
def prev_problem():
    problems_df = st.session_state.problems_df
    student_grade = st.session_state.user_data['grade']
    filtered_problems = problems_df[problems_df['학년'] == student_grade]
    
    if st.session_state.current_problem_index > 0:
        st.session_state.current_problem_index -= 1
    else:
        # 첫 문제인 경우 마지막 문제로 이동
        st.session_state.current_problem_index = len(filtered_problems) - 1

# 교사 대시보드
def teacher_dashboard():
    st.title(f"👨‍🏫 교사 대시보드 - {st.session_state.user_data['name']} 선생님")
    st.write("문제 관리 및 학생 성적 확인")
    
    tab1, tab2 = st.tabs(["문제 관리", "성적 통계"])
    
    with tab1:
        st.subheader("📝 문제 관리")
        
        # 기존 문제 표시
        problems_df = st.session_state.problems_df
        
        # 학년별 필터링
        grade_filter = st.selectbox("학년 필터링", ["전체"] + sorted(problems_df['학년'].unique().tolist()))
        
        if grade_filter != "전체":
            filtered_df = problems_df[problems_df['학년'] == grade_filter]
        else:
            filtered_df = problems_df
        
        if not filtered_df.empty:
            st.dataframe(filtered_df)
            st.success(f"총 {len(filtered_df)}개의 문제가 등록되어 있습니다.")
        else:
            st.info("현재 등록된 문제가 없습니다.")
            
    # 성적 통계 탭
    with tab2:
        st.subheader("📊 성적 통계")
        
        # 학생 답안 데이터 로드
        student_answers_df = st.session_state.answers_df
        
        if not student_answers_df.empty:
            st.dataframe(student_answers_df)
            
            # 간단한 통계
            if '점수' in student_answers_df.columns:
                avg_score = student_answers_df['점수'].mean()
                st.metric("평균 점수", f"{avg_score:.1f}점")
                
                # 학생별 평균 점수
                st.subheader("학생별 평균 점수")
                student_avg = student_answers_df.groupby('이름')['점수'].mean().reset_index()
                student_avg.columns = ['학생', '평균 점수']
                st.dataframe(student_avg)
        else:
            st.info("아직 제출된 학생 답안이 없습니다.")

# 학생 포털 함수 수정
def student_portal():
    st.title(f"👨‍🎓 {st.session_state.user_data['name']}님의 학습 포털")
    st.write(f"학년: {st.session_state.user_data['grade']}")
    
    tab1, tab2 = st.tabs(["문제 풀기", "내 성적"])
    
    with tab1:
        st.subheader("📝 문제 풀기")
        
        # 문제 목록 필터링 (학년별)
        problems_df = st.session_state.problems_df
        student_grade = st.session_state.user_data['grade']
        
        # 학년별 필터링
        filtered_problems = problems_df[problems_df['학년'] == student_grade]
        
        if filtered_problems.empty:
            st.warning(f"{student_grade} 학년에 해당하는 문제가 없습니다. 모든 문제를 표시합니다.")
            filtered_problems = problems_df
        
        if not filtered_problems.empty:
            # 문제 인덱스 확인 및 조정
            if st.session_state.current_problem_index >= len(filtered_problems):
                st.session_state.current_problem_index = 0
            
            # 진행 상태 표시
            total_problems = len(filtered_problems)
            current_index = st.session_state.current_problem_index + 1
            progress = current_index / total_problems
            st.progress(progress)
            st.write(f"문제 {current_index}/{total_problems}")
            
            # 현재 문제 가져오기
            current_problem = filtered_problems.iloc[st.session_state.current_problem_index]
            
            # 문제 표시
            st.markdown("<div class='problem-card'>", unsafe_allow_html=True)
            st.markdown(f"### 문제: {current_problem['문제내용']}")
            st.markdown(f"**난이도**: {current_problem['난이도']} | **유형**: {current_problem['문제유형']}")
            
            # 정답 입력란
            user_answer = ""
            
            # 객관식 문제인 경우 보기 표시
            if current_problem['문제유형'] == '객관식':
                options = []
                for i in range(1, 6):
                    option_key = f'보기{i}'
                    if current_problem[option_key] and isinstance(current_problem[option_key], str) and current_problem[option_key].strip():
                        options.append(current_problem[option_key])
                
                # 답안 선택
                user_answer = st.radio("답안 선택:", options, key=f"radio_{st.session_state.current_problem_index}")
            else:
                # 주관식 답안 입력
                user_answer = st.text_area("답안 작성:", height=100, placeholder="답변을 입력하세요...", key=f"text_{st.session_state.current_problem_index}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 네비게이션 버튼
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("← 이전 문제", key="prev_button"):
                    prev_problem()
                    st.rerun()
            
            # 다음 문제로 이동 및 제출 버튼
            with col3:
                # 마지막 문제가 아닐 경우에만 다음 문제 버튼 표시
                if current_index < total_problems:
                    if st.button("다음 문제 →", key="next_button"):
                        next_problem()
                        st.rerun()
            
            # 제출 버튼 - 마지막 문제에서만 표시
            with col2:
                # 마지막 문제일 경우에만 제출 버튼 표시
                submit_button = False
                if current_index == total_problems:
                    submit_button = st.button("제출하기", key="submit_button")
                
                if submit_button:
                    if user_answer:
                        # 채점
                        score, feedback = grade_answer(
                            current_problem['문제유형'], 
                            current_problem['정답'], 
                            user_answer, 
                            current_problem['키워드']
                        )
                        
                        # 결과 표시
                        st.markdown(f"### 채점 결과")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("점수", f"{score}점")
                        with col2:
                            st.metric("정답", current_problem['정답'])
                        
                        st.markdown("<div class='feedback-box'>", unsafe_allow_html=True)
                        st.markdown(f"**피드백**: {feedback}")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        if current_problem['해설']:
                            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                            st.markdown(f"**해설**: {current_problem['해설']}")
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        # 답안 저장
                        new_answer = {
                            '학생ID': st.session_state.user_data['username'],
                            '이름': st.session_state.user_data['name'],
                            '학년': st.session_state.user_data['grade'],
                            '문제ID': current_problem['문제ID'],
                            '제출답안': user_answer,
                            '점수': score,
                            '피드백': feedback,
                            '제출시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # 새 답안을 DataFrame에 추가
                        st.session_state.answers_df = pd.concat([
                            st.session_state.answers_df,
                            pd.DataFrame([new_answer])
                        ], ignore_index=True)
                        
                        # 결과 표시 후 첫 번째 문제로 되돌아가기
                        st.session_state.current_problem_index = 0
                        st.rerun()
                    else:
                        st.error("답안을 입력해주세요.")
        else:
            st.error("등록된 문제가 없습니다.")
    
    # 성적 확인 탭
    with tab2:
        st.subheader("📊 내 성적")
        
        # 현재 학생의 답안만 필터링
        student_answers = st.session_state.answers_df[
            st.session_state.answers_df['학생ID'] == st.session_state.user_data['username']
        ]
        
        if not student_answers.empty:
            # 평균 점수 계산
            avg_score = student_answers['점수'].mean()
            
            # 통계 표시
            st.metric("평균 점수", f"{avg_score:.1f}점")
            st.metric("제출한 문제 수", f"{len(student_answers)}개")
            
            # 문제별 점수 표시
            st.subheader("문제별 점수")
            display_df = student_answers[['문제ID', '제출답안', '점수', '피드백', '제출시간']]
            st.dataframe(display_df)
        else:
            st.info("아직 제출한 문제가 없습니다.")

# 로그인 화면
def login():
    st.title("🏫 학원 자동 첨삭 시스템")
    st.write("학생들의 영어 문제 풀이를 자동으로 채점하고 피드백을 제공합니다.")
    
    # 로그인 폼
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
        
        # Google Sheets 정보
        st.markdown("---")
        st.markdown("### Google Sheets 연동 정보")
        st.markdown(f"스프레드시트 ID: `{SPREADSHEET_ID}`")
        st.markdown(f"[Google Sheets 직접 열기](https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID})")

# 구글 시트 API 연결 확인 함수
def check_google_sheets_connection():
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        # 인증 파일 확인
        if not os.path.exists('credentials.json'):
            return False, "Google API 인증 파일(credentials.json)을 찾을 수 없습니다."
        
        # 서비스 계정 인증 시도
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        
        # 스프레드시트 ID 확인
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        title = sheet_metadata.get('properties', {}).get('title', '')
        
        return True, f"Google Sheets에 성공적으로 연결되었습니다. 스프레드시트: {title}"
    except ImportError:
        return False, "구글 API 라이브러리가 설치되지 않았습니다."
    except Exception as e:
        return False, f"Google Sheets 연결 오류: {str(e)}"

# 메인 앱 실행
def main():
    # 구글 시트 연결 확인
    sheets_connected, connection_message = check_google_sheets_connection()
    
    # 페이지 라우팅
    if not st.session_state.authenticated:
        # 로그인 화면에서는 사이드바 완전히 숨김
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {display: none;}
        </style>
        """, unsafe_allow_html=True)
        
        # 구글 시트 연결 상태 표시 - 화면 상단에 경고로 표시
        st.markdown("""
        <style>
        .connection-warning {
            background-color: #FFFCE9;
            padding: 8px 16px;
            border-radius: 8px;
            border-left: 4px solid #FFEB3B;
            margin-bottom: 16px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if not sheets_connected:
            st.markdown(f"""
            <div class="connection-warning">
                <p>Google Sheets에서 문제를 가져오지 못했습니다. 기본 문제를 사용합니다.</p>
                <p><small>이유: {connection_message}</small></p>
            </div>
            """, unsafe_allow_html=True)
        
        login()
    else:
        # 로그인 후에도 사이드바 완전히 숨김
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {display: none;}
        header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
        
        # 상단 네비게이션 바 생성
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"## 학원 자동 첨삭 시스템")
            
            # 구글 시트 연결 상태 표시 - 작게 표시
            if not sheets_connected:
                st.caption(f"⚠️ Google Sheets 연결 실패: 기본 샘플 문제를 사용합니다")
        with col2:
            st.write(f"사용자: {st.session_state.user_data['name']}")
        with col3:
            st.write(f"역할: {'선생님' if st.session_state.user_data['role'] == 'teacher' else '학생'}")
        with col4:
            if st.button("로그아웃", key="logout_top"):
                logout()
                st.rerun()
        
        st.markdown("---")
        
        # 페이지 내용 표시
        if st.session_state.user_data["role"] == "teacher":
            teacher_dashboard()
        else:
            student_portal()

if __name__ == "__main__":
    main() 