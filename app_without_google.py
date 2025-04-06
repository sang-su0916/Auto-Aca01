import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="학원 자동 첨삭 시스템",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# 사용자 데이터베이스 초기화
def initialize_user_db():
    # 사용자 데이터베이스 파일 확인
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 기본 사용자 데이터
        users = {
            "admin": {
                "password": "1234",
                "name": "관리자",
                "role": "teacher",
                "grade": "선생님"
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
        # 사용자 데이터 저장
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        return users

# 샘플 문제 초기화
def initialize_sample_questions():
    # CSV 파일이 있으면 로드, 없으면 생성
    if os.path.exists('sample_questions.csv'):
        try:
            return pd.read_csv('sample_questions.csv', encoding='utf-8')
        except Exception as e:
            st.error(f"샘플 문제 로드 오류: {str(e)}")
    
    # 기본 샘플 문제 생성
    questions = []
    
    # 중1 문제
    for i in range(1, 8):
        questions.append({
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중1',
            '문제유형': '객관식',
            '난이도': ['상', '중', '하'][i % 3],
            '문제내용': '다음 중 과일이 아닌 것은?',
            '보기1': '사과 (Apple)',
            '보기2': '바나나 (Banana)',
            '보기3': '당근 (Carrot)',
            '보기4': '오렌지 (Orange)',
            '보기5': '',
            '정답': '당근 (Carrot)',
            '키워드': 'fruit,vegetable',
            '해설': '당근(Carrot)은 채소(vegetable)입니다. 나머지는 모두 과일(fruit)입니다.'
        })
    
    # 중2 문제
    for i in range(8, 15):
        questions.append({
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중2',
            '문제유형': '객관식',
            '난이도': ['중', '상', '하'][i % 3],
            '문제내용': '다음 중 "남쪽"을 의미하는 영어 단어는?',
            '보기1': 'North',
            '보기2': 'East',
            '보기3': 'West',
            '보기4': 'South',
            '보기5': '',
            '정답': 'South',
            '키워드': 'direction,south',
            '해설': 'South는 남쪽, North는 북쪽, East는 동쪽, West는 서쪽을 의미합니다.'
        })
    
    # 중3 문제
    for i in range(15, 22):
        questions.append({
            '문제ID': f'P{i:03d}',
            '과목': '영어',
            '학년': '중3',
            '문제유형': '주관식',
            '난이도': ['상', '중', '하'][i % 3],
            '문제내용': '다음 문장의 빈칸에 알맞은 관사를 넣으세요: "I saw ___ elephant at the zoo."',
            '보기1': '',
            '보기2': '',
            '보기3': '',
            '보기4': '',
            '보기5': '',
            '정답': 'an',
            '키워드': 'article,an,vowel',
            '해설': '모음(a, e, i, o, u)으로 시작하는 단어 앞에는 부정관사 "an"을 사용합니다. Elephant는 "e"로 시작하므로 "an"을 사용합니다.'
        })
    
    # DataFrame 생성 및 저장
    df = pd.DataFrame(questions)
    try:
        df.to_csv('sample_questions.csv', index=False, encoding='utf-8')
    except Exception as e:
        st.error(f"샘플 문제 저장 오류: {str(e)}")
    
    return df

# 학생 답변 초기화
def initialize_student_answers():
    # CSV 파일이 있으면 로드, 없으면 생성
    if os.path.exists('student_answers.csv'):
        try:
            return pd.read_csv('student_answers.csv', encoding='utf-8')
        except Exception as e:
            st.error(f"학생 답변 로드 오류: {str(e)}")
    
    # 빈 DataFrame 생성 및 저장
    columns = ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
    df = pd.DataFrame(columns=columns)
    try:
        df.to_csv('student_answers.csv', index=False, encoding='utf-8')
    except Exception as e:
        st.error(f"학생 답변 저장 오류: {str(e)}")
    
    return df

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
                    feedback = f"더 정확한 답변이 필요합니다. 정답은 '{correct_answer}'입니다."
                return score, feedback
        
        # 기본 피드백
        return 0, f"오답입니다. 정답은 '{correct_answer}'입니다."
    
    return 0, "알 수 없는 문제 유형입니다."

# 사용자 인증
def authenticate_user(username, password):
    users = initialize_user_db()
    if username in users and users[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.user_data = {
            "username": username,
            "name": users[username]["name"],
            "role": users[username]["role"],
            "grade": users[username]["grade"]
        }
        return True
    return False

# 로그아웃
def logout():
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.session_state.current_problem_index = 0

# 다음 문제로 이동
def next_problem():
    if st.session_state.current_problem_index < len(st.session_state.problems) - 1:
        st.session_state.current_problem_index += 1

# 이전 문제로 이동
def prev_problem():
    if st.session_state.current_problem_index > 0:
        st.session_state.current_problem_index -= 1

# 교사 대시보드
def teacher_dashboard():
    st.title("교사 대시보드")
    
    # 문제 관리와 학생 답변 확인 탭
    tab1, tab2 = st.tabs(["문제 관리", "학생 답변 확인"])
    
    with tab1:
        st.header("문제 목록")
        
        # 문제 필터링
        cols = st.columns(4)
        with cols[0]:
            grade_filter = st.selectbox("학년 필터", ["전체"] + list(st.session_state.problems['학년'].unique()))
        with cols[1]:
            difficulty_filter = st.selectbox("난이도 필터", ["전체"] + list(st.session_state.problems['난이도'].unique()))
        with cols[2]:
            type_filter = st.selectbox("문제유형 필터", ["전체"] + list(st.session_state.problems['문제유형'].unique()))
        with cols[3]:
            search_query = st.text_input("검색어")
        
        # 필터 적용
        filtered_problems = st.session_state.problems.copy()
        if grade_filter != "전체":
            filtered_problems = filtered_problems[filtered_problems['학년'] == grade_filter]
        if difficulty_filter != "전체":
            filtered_problems = filtered_problems[filtered_problems['난이도'] == difficulty_filter]
        if type_filter != "전체":
            filtered_problems = filtered_problems[filtered_problems['문제유형'] == type_filter]
        if search_query:
            mask = filtered_problems.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)
            filtered_problems = filtered_problems[mask]
        
        # 문제 표시
        st.dataframe(
            filtered_problems[['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', '정답']],
            use_container_width=True
        )
        
        # 문제 상세 정보
        st.header("문제 상세 정보")
        selected_problem_id = st.selectbox("문제 선택", filtered_problems['문제ID'].tolist())
        if selected_problem_id:
            problem = filtered_problems[filtered_problems['문제ID'] == selected_problem_id].iloc[0]
            
            st.subheader(f"[{problem['난이도']}] {problem['문제내용']}")
            st.write(f"학년: {problem['학년']} | 과목: {problem['과목']} | 유형: {problem['문제유형']}")
            
            if problem['문제유형'] == '객관식':
                options = [problem['보기1'], problem['보기2'], problem['보기3'], problem['보기4']]
                options = [opt for opt in options if opt]  # 빈 값 제거
                st.write("보기:")
                for i, option in enumerate(options, 1):
                    st.write(f"{i}. {option}")
            
            st.write(f"**정답:** {problem['정답']}")
            st.write(f"**키워드:** {problem['키워드']}")
            st.write(f"**해설:** {problem['해설']}")
    
    with tab2:
        st.header("학생 답변 목록")
        
        if len(st.session_state.student_answers) > 0:
            # 학생 필터링
            cols = st.columns(3)
            with cols[0]:
                student_filter = st.selectbox(
                    "학생 필터", 
                    ["전체"] + list(st.session_state.student_answers['이름'].unique())
                )
            with cols[1]:
                problem_filter = st.selectbox(
                    "문제 필터", 
                    ["전체"] + list(st.session_state.student_answers['문제ID'].unique())
                )
            with cols[2]:
                score_filter = st.selectbox(
                    "점수 필터", 
                    ["전체", "100점", "80점 이상", "60점 이상", "60점 미만", "0점"]
                )
            
            # 필터 적용
            filtered_answers = st.session_state.student_answers.copy()
            if student_filter != "전체":
                filtered_answers = filtered_answers[filtered_answers['이름'] == student_filter]
            if problem_filter != "전체":
                filtered_answers = filtered_answers[filtered_answers['문제ID'] == problem_filter]
            if score_filter != "전체":
                if score_filter == "100점":
                    filtered_answers = filtered_answers[filtered_answers['점수'] == 100]
                elif score_filter == "80점 이상":
                    filtered_answers = filtered_answers[filtered_answers['점수'] >= 80]
                elif score_filter == "60점 이상":
                    filtered_answers = filtered_answers[filtered_answers['점수'] >= 60]
                elif score_filter == "60점 미만":
                    filtered_answers = filtered_answers[filtered_answers['점수'] < 60]
                elif score_filter == "0점":
                    filtered_answers = filtered_answers[filtered_answers['점수'] == 0]
            
            # 학생 답변 표시
            st.dataframe(
                filtered_answers[['이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']],
                use_container_width=True
            )
            
            # 학생 성적 통계
            st.header("학생 성적 통계")
            
            if len(filtered_answers) > 0:
                # 학생별 평균 점수
                student_avg = filtered_answers.groupby('이름')['점수'].mean().reset_index()
                student_avg.columns = ['학생', '평균 점수']
                st.bar_chart(student_avg.set_index('학생'))
                
                # 문제별 평균 점수
                problem_avg = filtered_answers.groupby('문제ID')['점수'].mean().reset_index()
                problem_avg.columns = ['문제ID', '평균 점수']
                st.bar_chart(problem_avg.set_index('문제ID'))
            else:
                st.info("필터링된 답변이 없습니다.")
        else:
            st.info("아직 제출된 학생 답변이 없습니다.")

# 학생 포털
def student_portal():
    st.title(f"{st.session_state.user_data['name']}님의 학습 포털")
    
    # 문제 목록과 풀기 탭
    tab1, tab2 = st.tabs(["문제 목록", "문제 풀기"])
    
    with tab1:
        st.header("영어 문제 목록")
        
        # 학년에 맞는 문제만 필터링
        student_grade = st.session_state.user_data['grade']
        student_problems = st.session_state.problems[st.session_state.problems['학년'] == student_grade]
        
        # 문제 난이도별 필터링
        difficulty_filter = st.selectbox("난이도 필터", ["전체"] + list(student_problems['난이도'].unique()), key="difficulty_filter")
        if difficulty_filter != "전체":
            student_problems = student_problems[student_problems['난이도'] == difficulty_filter]
        
        # 문제 목록 표시
        st.dataframe(
            student_problems[['문제ID', '과목', '난이도', '문제유형', '문제내용']],
            use_container_width=True
        )
        
        if len(student_problems) > 0:
            st.success(f"총 {len(student_problems)}개의 문제가 있습니다. '문제 풀기' 탭에서 풀어보세요!")
        else:
            st.warning(f"현재 {student_grade} 학년에 맞는 문제가 없습니다.")
    
    with tab2:
        # 현재 학년에 맞는 문제만 필터링
        student_grade = st.session_state.user_data['grade']
        student_problems = st.session_state.problems[st.session_state.problems['학년'] == student_grade]
        
        if len(student_problems) == 0:
            st.warning(f"현재 {student_grade} 학년에 맞는 문제가 없습니다.")
        else:
            # 현재 문제 인덱스 조정
            if st.session_state.current_problem_index >= len(student_problems):
                st.session_state.current_problem_index = 0
            
            student_problems_list = student_problems.to_dict('records')
            
            # 현재 문제
            current_problem = student_problems_list[st.session_state.current_problem_index]
            
            # 문제 표시
            st.subheader(f"문제 {st.session_state.current_problem_index + 1}/{len(student_problems_list)}")
            st.markdown(f"**난이도: {current_problem['난이도']}**")
            st.markdown(f"### {current_problem['문제내용']}")
            
            # 객관식인 경우 보기 표시
            if current_problem['문제유형'] == '객관식':
                options = []
                for i in range(1, 6):
                    option_key = f'보기{i}'
                    if option_key in current_problem and current_problem[option_key]:
                        options.append(current_problem[option_key])
                
                selected_option = st.radio("답을 선택하세요:", options, key=f"radio_{current_problem['문제ID']}")
                user_answer = selected_option
            else:
                user_answer = st.text_input("답을 입력하세요:", key=f"text_{current_problem['문제ID']}")
            
            # 이전/다음 버튼
            cols = st.columns(4)
            with cols[0]:
                if st.button("이전 문제", key="prev_btn"):
                    prev_problem()
                    st.rerun()
            with cols[1]:
                if st.button("다음 문제", key="next_btn"):
                    next_problem()
                    st.rerun()
            
            # 제출 버튼 (마지막 문제에서만 표시)
            is_last_question = st.session_state.current_problem_index == len(student_problems_list) - 1
            
            with cols[3]:
                if is_last_question and st.button("제출하기", key="submit_btn"):
                    # 자동 채점
                    score, feedback = grade_answer(
                        current_problem['문제유형'],
                        current_problem['정답'],
                        user_answer,
                        current_problem.get('키워드', '')
                    )
                    
                    # 결과 저장
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
                    
                    # 기존 답변에 추가
                    student_answers_df = st.session_state.student_answers.copy()
                    student_answers_df = pd.concat([student_answers_df, pd.DataFrame([new_answer])], ignore_index=True)
                    st.session_state.student_answers = student_answers_df
                    
                    # CSV 파일 저장
                    try:
                        student_answers_df.to_csv('student_answers.csv', index=False, encoding='utf-8')
                    except Exception as e:
                        st.error(f"답변 저장 오류: {str(e)}")
                    
                    # 결과 표시
                    st.success("답변이 제출되었습니다!")
                    st.info(f"점수: {score}")
                    st.write(f"피드백: {feedback}")
                    
                    if score < 100:
                        st.write(f"정답: {current_problem['정답']}")
                        st.write(f"해설: {current_problem['해설']}")

# 로그인 화면
def login():
    st.title("학원 자동 첨삭 시스템")
    st.subheader("학생들의 영어 문제 풀이를 자동으로 채점하고 피드백을 제공합니다.")
    
    # 로그인 폼
    with st.form("로그인"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submit = st.form_submit_button("로그인")
        
        if submit:
            if authenticate_user(username, password):
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
    
    # 기본 계정 정보
    st.markdown("### 기본 계정")
    st.markdown("- 교사: `admin` / `1234` (관리자, 선생님)")
    st.markdown("- 학생1: `student1` / `1234` (홍길동, 중3)")
    st.markdown("- 학생2: `student2` / `1234` (김철수, 중2)")
    st.markdown("- 학생3: `student3` / `1234` (박영희, 중1)")

# 메인 실행
def main():
    # CSS 스타일 추가
    st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    .css-18e3th9 {
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 로그인 확인
    if not st.session_state.authenticated:
        # 로그인 화면에서는 사이드바 완전히 숨김
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {display: none;}
        </style>
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
        with col2:
            st.write(f"사용자: {st.session_state.user_data['name']}")
        with col3:
            st.write(f"역할: {'선생님' if st.session_state.user_data['role'] == 'teacher' else '학생'}")
        with col4:
            if st.button("로그아웃", key="logout_top"):
                logout()
                st.rerun()
        
        st.markdown("---")
        
        # 데이터 로드
        if st.session_state.problems is None:
            st.session_state.problems = initialize_sample_questions()
        
        if st.session_state.student_answers is None:
            st.session_state.student_answers = initialize_student_answers()
        
        # 페이지 내용 표시
        if st.session_state.user_data["role"] == "teacher":
            teacher_dashboard()
        else:
            student_portal()

if __name__ == "__main__":
    # 사용자 데이터베이스 초기화
    initialize_user_db()
    
    # 앱 실행
    main() 