import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# 페이지 설정
st.set_page_config(page_title="학원 자동 첨삭 시스템", page_icon="📚")

# 사용자 계정 정보
USER_DB_FILE = "users.json"

# 사용자 DB 초기화
def initialize_user_db():
    if not os.path.exists(USER_DB_FILE):
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
        with open(USER_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=4)
    
    with open(USER_DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 사용자 데이터베이스 로드
users_db = initialize_user_db()

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

# CSV 파일 데이터 로드
def load_data():
    try:
        problems = pd.read_csv("sample_questions.csv", encoding="utf-8")
        answers = pd.read_csv("student_answers.csv", encoding="utf-8")
        return problems, answers
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return None, None

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
        problems_df, _ = load_data()
        if problems_df is not None and not problems_df.empty:
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
                    try:
                        # 기존 문제 로드
                        problems_df, _ = load_data()
                        
                        # 새 문제 추가
                        new_problem = pd.DataFrame([{
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
                            '정답': answer,
                            '키워드': keywords,
                            '해설': explanation
                        }])
                        
                        # 문제 추가 및 저장
                        if problems_df is None:
                            problems_df = new_problem
                        else:
                            problems_df = pd.concat([problems_df, new_problem], ignore_index=True)
                        
                        problems_df.to_csv('sample_questions.csv', index=False, encoding='utf-8')
                        st.success("문제가 성공적으로 추가되었습니다!")
                    except Exception as e:
                        st.error(f"문제 추가 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.error("필수 필드(문제ID, 과목, 학년, 문제 내용, 정답)를 모두 입력해주세요.")
    
    with tab2:
        st.subheader("📈 성적 통계")
        
        # 학생 답안 데이터 가져오기
        _, answers_df = load_data()
        
        if answers_df is not None and len(answers_df) > 1:
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
        else:
            st.info("아직 제출된 답안이 없습니다.")

# 학생 포털
def student_portal():
    st.title(f"👨‍🎓 학생 포털 - {st.session_state.user_data['name']} ({st.session_state.user_data['grade']})")
    
    # 문제 목록 표시
    st.subheader("📝 문제 목록")
    
    # 문제 데이터 로드
    problems_df, _ = load_data()
    
    if problems_df is not None and not problems_df.empty:
        for _, problem in problems_df.iterrows():
            with st.expander(f"{problem['문제ID']} - {problem['문제내용'][:30]}... ({problem['과목']}, {problem['학년']})"):
                st.subheader(problem['문제내용'])
                
                # 객관식 문제 표시
                if problem['문제유형'] == '객관식':
                    options = []
                    if not pd.isna(problem['보기1']) and problem['보기1']: options.append(problem['보기1'])
                    if not pd.isna(problem['보기2']) and problem['보기2']: options.append(problem['보기2'])
                    if not pd.isna(problem['보기3']) and problem['보기3']: options.append(problem['보기3'])
                    if not pd.isna(problem['보기4']) and problem['보기4']: options.append(problem['보기4'])
                    if not pd.isna(problem['보기5']) and problem['보기5']: options.append(problem['보기5'])
                    
                    user_answer = st.radio(
                        "답을 선택하세요:",
                        options,
                        key=f"radio_{problem['문제ID']}"
                    )
                else:
                    # 주관식 문제
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
                        problem['키워드'] if not pd.isna(problem['키워드']) else None
                    )
                    
                    # 결과 표시
                    st.success(f"채점 결과: {score}점")
                    st.info(f"피드백: {feedback}")
                    st.info(f"해설: {problem['해설']}")
                    
                    # CSV 파일에 저장
                    try:
                        # 기존 답안 데이터 로드
                        _, answers_df = load_data()
                        
                        # 새 답안 추가
                        new_answer = pd.DataFrame([{
                            '학생ID': st.session_state.user_data['username'],
                            '이름': st.session_state.user_data['name'],
                            '학년': st.session_state.user_data['grade'],
                            '문제ID': problem['문제ID'],
                            '제출답안': user_answer,
                            '점수': score,
                            '피드백': feedback,
                            '제출시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }])
                        
                        # 답안 추가 및 저장
                        if answers_df is None or answers_df.empty:
                            answers_df = new_answer
                        else:
                            answers_df = pd.concat([answers_df, new_answer], ignore_index=True)
                        
                        answers_df.to_csv('student_answers.csv', index=False, encoding='utf-8')
                        st.success("답안이 성공적으로 제출되었습니다!")
                    except Exception as e:
                        st.error(f"답안 저장 중 오류가 발생했습니다: {str(e)}")
    else:
        st.info("등록된 문제가 없습니다.")

# 로그인 화면
def login_screen():
    st.title("🏫 학원 자동 첨삭 시스템")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👨‍🏫 로그인")
        with st.form("login_form"):
            username = st.text_input("아이디", placeholder="아이디를 입력하세요")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            submit = st.form_submit_button("로그인")
            
            if submit:
                if authenticate_user(username, password):
                    st.success("로그인 성공!")
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 잘못되었습니다.")
    
    with col2:
        st.subheader("👨‍🏫 사용 안내")
        st.info("""
        **기본 계정**
        - **교사:** admin / 1234
        - **학생1:** student1 / 1234 (홍길동, 중3)
        - **학생2:** student2 / 1234 (김철수, 중2)
        """)
        
        st.write("### 로그인 후 이용할 수 있는 기능")
        st.write("#### 교사")
        st.write("- 문제 등록 및 관리")
        st.write("- 학생 답안 및 성적 확인")
        
        st.write("#### 학생")
        st.write("- 문제 풀기")
        st.write("- 자동 채점 및 피드백 확인")

# 메인 페이지 라우팅
def main():
    # 사이드바 - 로그인 정보 및 로그아웃 버튼
    if st.session_state.authenticated:
        with st.sidebar:
            st.markdown(f"### {st.session_state.user_data['name']}님 환영합니다")
            st.markdown(f"**역할:** {'교사' if st.session_state.user_data['role'] == 'teacher' else '학생'}")
            
            if st.session_state.user_data['role'] == 'student':
                st.markdown(f"**학년:** {st.session_state.user_data['grade']}")
            
            if st.button("로그아웃"):
                logout()
                st.rerun()
    
    # 페이지 라우팅
    if not st.session_state.authenticated:
        login_screen()
    elif st.session_state.page == "teacher":
        teacher_dashboard()
    elif st.session_state.page == "student":
        student_portal()

if __name__ == "__main__":
    main()
