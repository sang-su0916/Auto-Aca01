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
    initial_sidebar_state="expanded"
)

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
        }
    }
    return default_users

# 사용자 데이터베이스 로드
users_db = initialize_user_db()

# 기본 데이터 초기화
def initialize_sample_questions():
    return pd.DataFrame([
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
        
        # 문제 추가 처리
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
            
            # 새 문제를 DataFrame에 추가
            st.session_state.problems_df = pd.concat([
                st.session_state.problems_df, 
                pd.DataFrame([new_problem])
            ], ignore_index=True)
            
            st.success(f"문제 '{problem_id}'가 성공적으로 추가되었습니다!")
            
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

# 학생 포털
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
            # 문제 선택
            problem_ids = filtered_problems['문제ID'].tolist()
            problem_contents = filtered_problems['문제내용'].tolist()
            problem_display = [f"{pid} - {content[:30]}..." for pid, content in zip(problem_ids, problem_contents)]
            
            selected_problem_display = st.selectbox("문제 선택", problem_display)
            selected_problem_id = selected_problem_display.split(' - ')[0]
            
            # 선택한 문제 정보
            problem = filtered_problems[filtered_problems['문제ID'] == selected_problem_id].iloc[0]
            
            # 문제 표시
            st.markdown(f"### 문제: {problem['문제내용']}")
            st.markdown(f"**난이도**: {problem['난이도']} | **유형**: {problem['문제유형']}")
            
            # 객관식 문제인 경우 보기 표시
            if problem['문제유형'] == '객관식':
                options = []
                for i in range(1, 6):
                    option_key = f'보기{i}'
                    if problem[option_key] and isinstance(problem[option_key], str) and problem[option_key].strip():
                        options.append(problem[option_key])
                
                # 답안 선택
                user_answer = st.radio("답안 선택", options)
            else:
                # 주관식 답안 입력
                user_answer = st.text_area("답안 작성", height=100, placeholder="답변을 입력하세요...")
            
            # 제출 버튼
            if st.button("제출하기"):
                if user_answer:
                    # 채점
                    score, feedback = grade_answer(
                        problem['문제유형'], 
                        problem['정답'], 
                        user_answer, 
                        problem['키워드']
                    )
                    
                    # 결과 표시
                    st.markdown(f"### 채점 결과")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("점수", f"{score}점")
                    with col2:
                        st.metric("정답", problem['정답'])
                    
                    st.markdown("<div class='feedback-box'>", unsafe_allow_html=True)
                    st.markdown(f"**피드백**: {feedback}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if problem['해설']:
                        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                        st.markdown(f"**해설**: {problem['해설']}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # 답안 저장
                    new_answer = {
                        '학생ID': st.session_state.user_data['username'],
                        '이름': st.session_state.user_data['name'],
                        '학년': st.session_state.user_data['grade'],
                        '문제ID': selected_problem_id,
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

# 메인 앱 실행
def main():
    # 로그아웃 버튼 (인증된 경우에만)
    if st.session_state.authenticated:
        if st.sidebar.button("로그아웃"):
            logout()
            st.rerun()
        
        st.sidebar.write(f"사용자: {st.session_state.user_data['name']}")
        st.sidebar.write(f"역할: {'선생님' if st.session_state.user_data['role'] == 'teacher' else '학생'}")
    
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