import streamlit as st
import pandas as pd
import os
import datetime
import json

# 페이지 설정
st.set_page_config(page_title="학원 자동 첨삭 시스템", page_icon="📚")

# 데이터 초기화
if not os.path.exists("sample_questions.csv"):
    initial_problems = pd.DataFrame({
        '문제ID': ['P001', 'P002', 'P003'],
        '과목': ['영어', '영어', '영어'],
        '학년': ['중2', '중3', '중3'],
        '문제유형': ['객관식', '객관식', '주관식'],
        '난이도': ['하', '중', '상'],
        '문제내용': ['다음 중 "책"을 의미하는 영어 단어는?', '다음 문장의 빈칸에 들어갈 말로 가장 적절한 것은? "I ___ to school every day."', '다음 문장을 영작하시오: "나는 어제 영화를 보았다."'],
        '보기1': ['apple', 'go', ''],
        '보기2': ['book', 'going', ''],
        '보기3': ['car', 'goes', ''],
        '보기4': ['desk', 'went', ''],
        '보기5': ['', '', ''],
        '정답': ['2', '1', 'I watched a movie yesterday.'],
        '키워드': ['book', 'go', 'watched,movie,yesterday'],
        '해설': ['book은 책을 의미합니다.', 'go는 "가다"라는 의미의 동사입니다.', '"watch"는 영화를 보다라는 의미이며, 과거형은 "watched"입니다.']
    })
    initial_problems.to_csv("sample_questions.csv", index=False, encoding='utf-8')

if not os.path.exists("student_answers.csv"):
    initial_answers = pd.DataFrame({
        '학생ID': ['S001', 'S002'],
        '이름': ['홍길동', '김철수'],
        '학년': ['중3', '중2'],
        '문제ID': ['P001', 'P002'],
        '제출답안': ['2', '1'],
        '점수': [100, 100],
        '피드백': ['정답입니다!', '정답입니다!'],
        '제출시간': [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    initial_answers.to_csv("student_answers.csv", index=False, encoding='utf-8')

# 사용자 계정 정보
USER_DB = {
    "admin": {
        "password": "1234",
        "name": "관리자",
        "role": "teacher"
    },
    "student1": {
        "password": "1234",
        "name": "홍길동",
        "role": "student",
        "grade": "중3",
        "id": "S001"
    },
    "student2": {
        "password": "1234",
        "name": "김철수",
        "role": "student",
        "grade": "중2",
        "id": "S002"
    }
}

# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "page" not in st.session_state:
    st.session_state.page = "login"

# 데이터 불러오기
def load_data():
    try:
        problems = pd.read_csv("sample_questions.csv", encoding='utf-8')
        answers = pd.read_csv("student_answers.csv", encoding='utf-8')
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
        
        return 0, f"오답입니다. 정답은 '{correct_answer}'입니다."
    
    return 0, "알 수 없는 문제 유형입니다."

# 사용자 인증
def login():
    st.title("🏫 학원 자동 첨삭 시스템")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👨‍🏫 로그인")
        with st.form("login_form"):
            username = st.text_input("아이디", placeholder="아이디를 입력하세요")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            submit = st.form_submit_button("로그인")
            
            if submit:
                if username in USER_DB and USER_DB[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.user_data = {
                        "username": username,
                        "name": USER_DB[username]["name"],
                        "role": USER_DB[username]["role"]
                    }
                    
                    if USER_DB[username]["role"] == "student":
                        st.session_state.user_data["grade"] = USER_DB[username]["grade"]
                        st.session_state.user_data["student_id"] = USER_DB[username]["id"]
                    
                    st.session_state.page = USER_DB[username]["role"]
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

# 로그아웃 함수
def logout():
    st.session_state.authenticated = False
    st.session_state.user_data = {}
    st.session_state.page = "login"
    st.rerun()

# 교사 대시보드
def teacher_dashboard():
    st.title(f"👨‍🏫 교사 대시보드 - {st.session_state.user_data['name']} 선생님")
    
    tab1, tab2 = st.tabs(["문제 관리", "성적 통계"])
    
    with tab1:
        st.subheader("📝 문제 관리")
        
        problems_df, _ = load_data()
        if problems_df is not None and not problems_df.empty:
            st.dataframe(problems_df)
            st.success(f"총 {len(problems_df)}개의 문제가 등록되어 있습니다.")
        else:
            st.info("문제가 아직 없습니다.")
    
    with tab2:
        st.subheader("📊 성적 통계")
        
        _, answers_df = load_data()
        if answers_df is not None and not answers_df.empty:
            st.dataframe(answers_df)
            
            avg_score = answers_df['점수'].mean()
            st.metric("평균 점수", f"{avg_score:.1f}")
            
            student_stats = answers_df.groupby(['이름', '학년'])['점수'].mean().reset_index()
            st.subheader("학생별 평균 점수")
            st.dataframe(student_stats)
        else:
            st.info("제출된 답안이 없습니다.")

# 학생 포털
def student_portal():
    st.title(f"👨‍🎓 학생 포털 - {st.session_state.user_data['name']} ({st.session_state.user_data['grade']})")
    
    tab1, tab2 = st.tabs(["문제 풀기", "내 성적"])
    
    with tab1:
        st.subheader("📝 문제 풀기")
        
        problems_df, _ = load_data()
        if problems_df is not None and not problems_df.empty:
            selected_problem = st.selectbox("문제 선택", range(len(problems_df)), 
                                       format_func=lambda i: f"{problems_df.iloc[i]['문제ID']} - {problems_df.iloc[i]['과목']} ({problems_df.iloc[i]['학년']})")
            
            if selected_problem is not None:
                problem = problems_df.iloc[selected_problem]
                
                st.subheader(problem['문제내용'])
                
                if problem['문제유형'] == '객관식':
                    options = []
                    for i in range(1, 6):
                        if not pd.isna(problem[f'보기{i}']) and problem[f'보기{i}'] != "":
                            options.append(f"{i}. {problem[f'보기{i}']}")
                    
                    for option in options:
                        st.write(option)
                
                with st.form("answer_form"):
                    if problem['문제유형'] == '객관식':
                        answer = st.text_input("답안 (번호만 입력)")
                    else:
                        answer = st.text_area("답안")
                    
                    submit = st.form_submit_button("제출")
                    
                    if submit:
                        if answer:
                            score, feedback = grade_answer(
                                problem['문제유형'],
                                problem['정답'],
                                answer,
                                problem['키워드']
                            )
                            
                            if score >= 80:
                                st.success(f"점수: {score} - {feedback}")
                            elif score >= 50:
                                st.warning(f"점수: {score} - {feedback}")
                            else:
                                st.error(f"점수: {score} - {feedback}")
                            
                            # 학생 답안 저장
                            try:
                                _, answers_df = load_data()
                                
                                new_answer = pd.DataFrame([{
                                    '학생ID': st.session_state.user_data['student_id'],
                                    '이름': st.session_state.user_data['name'],
                                    '학년': st.session_state.user_data['grade'],
                                    '문제ID': problem['문제ID'],
                                    '제출답안': answer,
                                    '점수': score,
                                    '피드백': feedback,
                                    '제출시간': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }])
                                
                                if answers_df is None:
                                    answers_df = new_answer
                                else:
                                    answers_df = pd.concat([answers_df, new_answer], ignore_index=True)
                                
                                answers_df.to_csv('student_answers.csv', index=False, encoding='utf-8')
                                st.info("답안이 저장되었습니다.")
                            except Exception as e:
                                st.error(f"답안 저장 중 오류가 발생했습니다: {e}")
                        else:
                            st.error("답안을 입력해주세요.")
        else:
            st.info("등록된 문제가 없습니다.")
    
    with tab2:
        st.subheader("📊 나의 성적")
        
        _, answers_df = load_data()
        if answers_df is not None and not answers_df.empty:
            student_answers = answers_df[answers_df['학생ID'] == st.session_state.user_data['student_id']]
            
            if not student_answers.empty:
                st.dataframe(student_answers)
                
                avg_score = student_answers['점수'].mean()
                st.metric("평균 점수", f"{avg_score:.1f}")
            else:
                st.info("제출한 답안이 없습니다.")
        else:
            st.info("제출한 답안이 없습니다.")

# 메인 함수
def main():
    # 사이드바에 로그아웃 버튼
    if st.session_state.authenticated:
        with st.sidebar:
            st.write(f"로그인: {st.session_state.user_data['name']}")
            if st.button("로그아웃"):
                logout()
    
    # 페이지 라우팅
    if not st.session_state.authenticated:
        login()
    elif st.session_state.page == "teacher":
        teacher_dashboard()
    elif st.session_state.page == "student":
        student_portal()
    else:
        login()

if __name__ == "__main__":
    main() 