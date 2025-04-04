import streamlit as st
import os
import pandas as pd
import base64
from datetime import datetime
import time
import json

# 페이지 설정 - 사이드바 기본적으로 숨김
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

# CSV 파일 기반 데이터 로드
def load_csv_data():
    try:
        # 샘플 문제 파일 생성 (없는 경우)
        if not os.path.exists('sample_questions.csv'):
            create_sample_questions()
            
        problems_df = pd.read_csv('sample_questions.csv')
        
        # 학생 답안 파일 생성 (없는 경우)
        if not os.path.exists('student_answers.csv'):
            student_answers_df = pd.DataFrame(columns=[
                '학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간'
            ])
            student_answers_df.to_csv('student_answers.csv', index=False)
        else:
            student_answers_df = pd.read_csv('student_answers.csv')
            
        return problems_df, student_answers_df
    except Exception as e:
        st.error(f"CSV 파일 로드 오류: {str(e)}")
        return None, None

# 샘플 문제 데이터 생성
def create_sample_questions():
    sample_questions = pd.DataFrame([
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
            '학년': '중3',
            '문제유형': '객관식',
            '난이도': '하',
            '문제내용': 'Which word means "house"?',
            '보기1': 'home',
            '보기2': 'car',
            '보기3': 'book',
            '보기4': 'pen',
            '보기5': '',
            '정답': 'home',
            '키워드': 'house,home,residence',
            '해설': '"home"은 "house"와 같은 의미로 사용됩니다.'
        }
    ])
    sample_questions.to_csv('sample_questions.csv', index=False)

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

# 데이터 로드
problems_df, answers_df = load_csv_data()
if problems_df is not None:
    st.session_state.problems_df = problems_df
else:
    st.session_state.problems_df = pd.DataFrame()

if answers_df is not None:
    st.session_state.answers_df = answers_df
else:
    st.session_state.answers_df = pd.DataFrame(columns=[
        '학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간'
    ])

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
    /* 스트림릿 사이드바 토글 버튼 숨기기 */
    .css-1rs6os {
        visibility: hidden;
    }
    .css-1dp5vir {
        visibility: hidden;
    }
    /* 로그인 폼 스타일 */
    .login-form {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    /* 헤더 스타일 */
    .header-style {
        color: #1e3a8a;
        margin-bottom: 1.5rem;
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

# 파일 저장 함수
def save_data():
    try:
        st.session_state.problems_df.to_csv('sample_questions.csv', index=False)
        st.session_state.answers_df.to_csv('student_answers.csv', index=False)
    except Exception as e:
        st.error(f"데이터 저장 오류: {str(e)}")

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

# 교사 대시보드
def teacher_dashboard():
    st.title(f"👨‍🏫 교사 대시보드 - {st.session_state.user_data['name']} 선생님")
    st.write("문제 관리 및 학생 성적 확인")
    
    tab1, tab2 = st.tabs(["문제 관리", "성적 통계"])
    
    with tab1:
        st.subheader("📝 문제 관리")
        
        # 기존 문제 표시
        problems_df = st.session_state.problems_df
        
        if not problems_df.empty:
            st.dataframe(problems_df)
            st.success(f"총 {len(problems_df)}개의 문제가 등록되어 있습니다.")
        else:
            st.info("현재 등록된 문제가 없습니다.")
        
        # 문제 추가 폼
        st.subheader("📝 문제 직접 추가")
        with st.form("add_problem_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                problem_id = st.text_input("문제ID", value="P" + datetime.now().strftime("%Y%m%d%H%M%S"))
                subject = st.selectbox("과목", ["영어", "수학", "국어", "과학", "사회"])
            with col2:
                grade = st.selectbox("학년", ["중1", "중2", "중3", "고1", "고2", "고3"])
                problem_type = st.selectbox("문제유형", ["객관식", "주관식"])
            with col3:
                difficulty = st.selectbox("난이도", ["상", "중", "하"])
            
            problem_content = st.text_area("문제 내용", placeholder="문제 내용을 입력하세요.")
            
            if problem_type == "객관식":
                col1, col2 = st.columns(2)
                with col1:
                    option1 = st.text_input("보기1")
                    option2 = st.text_input("보기2")
                    option3 = st.text_input("보기3")
                with col2:
                    option4 = st.text_input("보기4")
                    option5 = st.text_input("보기5", help="선택 사항")
            else:
                option1 = option2 = option3 = option4 = option5 = ""
            
            correct_answer = st.text_input("정답")
            keywords = st.text_input("키워드 (쉼표로 구분)", help="주관식 문제의 부분 점수 계산에 사용됩니다.")
            explanation = st.text_area("해설", placeholder="문제 해설을 입력하세요.")
            
            submit_button = st.form_submit_button("문제 추가")
            
            if submit_button and problem_content and correct_answer:
                new_problem = {
                    '문제ID': problem_id,
                    '과목': subject,
                    '학년': grade,
                    '문제유형': problem_type,
                    '난이도': difficulty,
                    '문제내용': problem_content,
                    '보기1': option1,
                    '보기2': option2,
                    '보기3': option3,
                    '보기4': option4,
                    '보기5': option5,
                    '정답': correct_answer,
                    '키워드': keywords,
                    '해설': explanation
                }
                
                st.session_state.problems_df = pd.concat([st.session_state.problems_df, pd.DataFrame([new_problem])], ignore_index=True)
                save_data()  # 데이터 저장
                st.success("문제가 추가되었습니다.")
                st.rerun()
    
    with tab2:
        st.subheader("📊 학생 성적 통계")
        
        answers_df = st.session_state.answers_df
        
        if not answers_df.empty:
            st.dataframe(answers_df)
            
            # 학생별 평균 점수
            student_scores = answers_df.groupby(['학생ID', '이름', '학년'])['점수'].agg(['mean', 'count']).reset_index()
            student_scores.columns = ['학생ID', '이름', '학년', '평균점수', '제출수']
            student_scores['평균점수'] = student_scores['평균점수'].round(2)
            
            st.subheader("학생별 성적")
            st.dataframe(student_scores)
            
            # 문제별 정답률
            problem_stats = answers_df.groupby('문제ID').agg({
                '점수': ['mean', 'count']
            }).reset_index()
            problem_stats.columns = ['문제ID', '평균점수', '응시수']
            problem_stats['평균점수'] = problem_stats['평균점수'].round(2)
            
            st.subheader("문제별 정답률")
            st.dataframe(problem_stats)
            
        else:
            st.info("아직 제출된 답안이 없습니다.")

# 학생 포털
def student_portal():
    st.title(f"👋 안녕하세요, {st.session_state.user_data['name']} 학생!")
    st.write(f"학년: {st.session_state.user_data['grade']}")
    
    tab1, tab2 = st.tabs(["문제 풀기", "나의 성적"])
    
    with tab1:
        st.subheader("📝 문제 풀기")
        
        # 필터 옵션
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_subject = st.selectbox("과목 선택", ["전체"] + sorted(st.session_state.problems_df['과목'].unique().tolist()))
        with col2:
            selected_grade = st.selectbox("학년 선택", ["전체"] + sorted(st.session_state.problems_df['학년'].unique().tolist()))
        with col3:
            selected_difficulty = st.selectbox("난이도", ["전체", "상", "중", "하"])
        
        # 필터링
        filtered_df = st.session_state.problems_df.copy()
        if selected_subject != "전체":
            filtered_df = filtered_df[filtered_df['과목'] == selected_subject]
        if selected_grade != "전체":
            filtered_df = filtered_df[filtered_df['학년'] == selected_grade]
        if selected_difficulty != "전체":
            filtered_df = filtered_df[filtered_df['난이도'] == selected_difficulty]
        
        if not filtered_df.empty:
            # 문제 선택
            problem_id = st.selectbox("문제 선택", filtered_df['문제ID'].tolist(), 
                                     format_func=lambda x: f"{x} - {filtered_df[filtered_df['문제ID'] == x].iloc[0]['문제내용'][:30]}...")
            
            selected_problem = filtered_df[filtered_df['문제ID'] == problem_id].iloc[0]
            
            # 문제 표시
            st.markdown(f"### 문제: {selected_problem['문제내용']}")
            st.write(f"과목: {selected_problem['과목']} | 난이도: {selected_problem['난이도']} | 유형: {selected_problem['문제유형']}")
            
            # 객관식 보기 표시
            if selected_problem['문제유형'] == '객관식':
                options = []
                for i in range(1, 6):
                    option = selected_problem[f'보기{i}']
                    if option and not pd.isna(option) and option.strip():
                        options.append(option)
                
                user_answer = st.radio("보기", options, key=f"radio_{problem_id}")
            else:
                user_answer = st.text_area("답변 작성", key=f"text_{problem_id}")
            
            if st.button("제출"):
                if user_answer:
                    # 채점
                    score, feedback = grade_answer(
                        selected_problem['문제유형'],
                        selected_problem['정답'],
                        user_answer,
                        selected_problem['키워드']
                    )
                    
                    # 결과 저장
                    new_answer = {
                        '학생ID': st.session_state.user_data['username'],
                        '이름': st.session_state.user_data['name'],
                        '학년': st.session_state.user_data['grade'],
                        '문제ID': problem_id,
                        '제출답안': user_answer,
                        '점수': score,
                        '피드백': feedback,
                        '제출시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.session_state.answers_df = pd.concat([st.session_state.answers_df, pd.DataFrame([new_answer])], ignore_index=True)
                    save_data()  # 데이터 저장
                    
                    # 결과 표시
                    st.markdown(f"""
                    <div class="result-card">
                        <h3>채점 결과</h3>
                        <p>점수: {score}/100</p>
                        <div class="feedback-box">
                            <p><strong>피드백:</strong> {feedback}</p>
                        </div>
                        <p><strong>해설:</strong> {selected_problem['해설']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("답안을 입력해주세요.")
        else:
            st.info("선택한 조건에 맞는 문제가 없습니다.")
    
    with tab2:
        st.subheader("📊 나의 성적")
        
        # 현재 학생의 답안만 필터링
        student_answers = st.session_state.answers_df[st.session_state.answers_df['학생ID'] == st.session_state.user_data['username']]
        
        if not student_answers.empty:
            st.dataframe(student_answers[['문제ID', '제출답안', '점수', '피드백', '제출시간']])
            
            avg_score = student_answers['점수'].mean()
            st.metric("평균 점수", f"{avg_score:.2f}/100")
            
            # 과목별 통계
            if '과목' in st.session_state.problems_df.columns:
                # 문제 데이터프레임에서 문제ID와 과목만 추출
                problem_subjects = st.session_state.problems_df[['문제ID', '과목']]
                
                # 학생 답안과 병합
                merged_df = pd.merge(student_answers, problem_subjects, on='문제ID')
                
                # 과목별 통계 계산
                subject_stats = merged_df.groupby('과목').agg({
                    '점수': ['mean', 'count']
                }).reset_index()
                
                subject_stats.columns = ['과목', '평균점수', '제출수']
                subject_stats['평균점수'] = subject_stats['평균점수'].round(2)
                
                st.subheader("과목별 성적")
                st.dataframe(subject_stats)
        else:
            st.info("아직 제출한 답안이 없습니다.")

# 로그인 화면
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;' class='header-style'>📚 학원 자동 첨삭 시스템</h1>", unsafe_allow_html=True)
        st.markdown("<div class='login-form'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>로그인</h2>", unsafe_allow_html=True)
        
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        
        login_btn = st.button("로그인", use_container_width=True)
        
        if login_btn:
            if authenticate_user(username, password):
                st.success(f"{st.session_state.user_data['name']}님, 로그인 성공!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3>데모 계정</h3>", unsafe_allow_html=True)
        st.markdown("""
        **교사 계정**
        - 아이디: admin
        - 비밀번호: 1234
        
        **학생 계정**
        - 아이디: student1 (홍길동, 중3)
        - 아이디: student2 (김철수, 중2)
        - 비밀번호: 1234
        """)
        st.markdown("</div>", unsafe_allow_html=True)

# 메인 앱 로직
def main():
    # 사이드바 - 로그인 정보 및 로그아웃 버튼
    if st.session_state.authenticated:
        with st.sidebar:
            st.write(f"**로그인 정보**")
            st.write(f"이름: {st.session_state.user_data['name']}")
            st.write(f"역할: {'교사' if st.session_state.user_data['role'] == 'teacher' else '학생'}")
            if st.session_state.user_data['grade']:
                st.write(f"학년: {st.session_state.user_data['grade']}")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            if st.button("로그아웃", use_container_width=True):
                logout()
                st.rerun()
    
    # 페이지 라우팅
    if not st.session_state.authenticated:
        login_screen()
    else:
        if st.session_state.user_data["role"] == "teacher":
            teacher_dashboard()
        else:
            student_portal()

# 앱 실행
if __name__ == "__main__":
    main() 