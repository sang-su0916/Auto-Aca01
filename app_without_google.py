import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# 페이지 설정
st.set_page_config(page_title="학원 자동 첨삭 시스템", page_icon="📚")

# 사용자 계정 정보 파일
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

# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "username": "",
        "name": "",
        "role": "",
        "grade": ""
    }
if "page" not in st.session_state:
    st.session_state.page = "login"

# 샘플 문제 및 학생 답변 초기화
def initialize_sample_data():
    # 샘플 문제 데이터
    if not os.path.exists("sample_questions.csv"):
        sample_questions = pd.DataFrame({
            '문제ID': ['P001', 'P002', 'P003', 'P004', 'P005'],
            '과목': ['영어', '영어', '영어', '영어', '영어'],
            '학년': ['중3', '중3', '중2', '고1', '고2'],
            '문제유형': ['객관식', '주관식', '객관식', '객관식', '주관식'],
            '난이도': ['중', '중', '하', '상', '중'],
            '문제내용': [
                '다음 중 "책"을 의미하는 영어 단어는?', 
                'Write a sentence using the word "beautiful".', 
                'Which word is a verb?', 
                'Choose the correct sentence.', 
                'What does "procrastination" mean?'
            ],
            '보기1': ['apple', '', 'happy', 'I have been to Paris last year.', ''],
            '보기2': ['book', '', 'book', 'I went to Paris last year.', ''],
            '보기3': ['car', '', 'run', 'I have went to Paris last year.', ''],
            '보기4': ['desk', '', 'fast', 'I go to Paris last year.', ''],
            '보기5': ['', '', '', '', ''],
            '정답': ['2', 'The flower is beautiful.', '3', '2', 'Delaying or postponing tasks'],
            '키워드': ['book', 'beautiful,sentence', 'verb,part of speech', 'grammar,past tense', 'vocabulary,meaning'],
            '해설': [
                'book은 책을 의미합니다.', 
                '주어와 동사를 포함한 완전한 문장이어야 합니다.', 
                '동사(verb)는 행동이나 상태를 나타내는 품사입니다. run(달리다)은 동사입니다.', 
                '과거에 일어난 일에는 과거 시제(went)를 사용합니다.', 
                'Procrastination은 일이나 활동을 미루는 행동을 의미합니다.'
            ]
        })
        sample_questions.to_csv("sample_questions.csv", index=False, encoding='utf-8')
    
    # 샘플 학생 답변 데이터
    if not os.path.exists("student_answers.csv"):
        sample_answers = pd.DataFrame({
            '학생ID': ['S001', 'S002', 'S001'],
            '이름': ['홍길동', '김철수', '홍길동'],
            '학년': ['중3', '중2', '중3'],
            '문제ID': ['P001', 'P003', 'P002'],
            '제출답안': ['2', '3', 'The sky is beautiful.'],
            '점수': [100, 100, 100],
            '피드백': ['정답입니다!', '정답입니다!', '정답입니다! 키워드를 모두 포함했습니다.'],
            '제출시간': [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        })
        sample_answers.to_csv("student_answers.csv", index=False, encoding='utf-8')

# 데이터 로드 함수
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

# 답안 저장 함수
def save_answer(student_id, name, grade, problem_id, answer, score, feedback):
    try:
        _, answers_df = load_data()
        
        new_answer = pd.DataFrame([{
            '학생ID': student_id,
            '이름': name,
            '학년': grade,
            '문제ID': problem_id,
            '제출답안': answer,
            '점수': score,
            '피드백': feedback,
            '제출시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        if answers_df is None:
            answers_df = new_answer
        else:
            answers_df = pd.concat([answers_df, new_answer], ignore_index=True)
        
        answers_df.to_csv('student_answers.csv', index=False, encoding='utf-8')
        return True
    except Exception as e:
        st.error(f"답안 저장 오류: {e}")
        return False

# 사용자 인증 함수
def authenticate_user(username, password):
    users_db = initialize_user_db()
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
        
        if answers_df is not None and len(answers_df) > 0:
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
            
            # 학생별 통계
            st.subheader("학생별 평균 점수")
            student_stats = answers_df.groupby(['학생ID', '이름', '학년'])['점수'].mean().reset_index()
            st.dataframe(student_stats)
        else:
            st.info("학생 답안 데이터가 없습니다.")

# 학생 포털
def student_portal():
    st.title(f"👨‍🎓 학생 포털 - {st.session_state.user_data['name']} ({st.session_state.user_data['grade']})")
    
    tab1, tab2 = st.tabs(["문제 풀기", "내 성적"])
    
    with tab1:
        st.subheader("📝 문제 풀기")
        
        problems_df, answers_df = load_data()
        
        if problems_df is not None and not problems_df.empty:
            # 필터링 옵션
            col1, col2, col3 = st.columns(3)
            
            with col1:
                subject_filter = st.selectbox("과목", ["전체"] + list(problems_df['과목'].unique()))
            with col2:
                grade_filter = st.selectbox("학년", ["전체"] + list(problems_df['학년'].unique()))
            with col3:
                difficulty_filter = st.selectbox("난이도", ["전체"] + list(problems_df['난이도'].unique()))
            
            # 필터 적용
            filtered_df = problems_df.copy()
            if subject_filter != "전체":
                filtered_df = filtered_df[filtered_df['과목'] == subject_filter]
            if grade_filter != "전체":
                filtered_df = filtered_df[filtered_df['학년'] == grade_filter]
            if difficulty_filter != "전체":
                filtered_df = filtered_df[filtered_df['난이도'] == difficulty_filter]
            
            # 이미 풀었는지 확인하기 위한 데이터 준비
            solved_problems = []
            if answers_df is not None and not answers_df.empty:
                # 현재 로그인한 학생이 이미 풀었던 문제 ID 목록
                solved_problems = answers_df[answers_df['학생ID'] == st.session_state.user_data['username']]['문제ID'].unique().tolist()
            
            # 문제 선택
            if not filtered_df.empty:
                st.write(f"{len(filtered_df)}개의 문제가 있습니다.")
                
                # 문제 목록 생성
                problems_list = []
                for _, row in filtered_df.iterrows():
                    status = "✅ " if row['문제ID'] in solved_problems else ""
                    problems_list.append(f"{status}{row['문제ID']} - {row['과목']} ({row['난이도']}) {row['문제내용'][:20]}...")
                
                selected_problem_idx = st.selectbox("문제 선택", range(len(problems_list)), format_func=lambda x: problems_list[x])
                
                if selected_problem_idx is not None:
                    selected_problem = filtered_df.iloc[selected_problem_idx]
                    
                    # 문제 표시
                    st.markdown("---")
                    st.subheader(f"문제 ID: {selected_problem['문제ID']}")
                    st.write(f"**과목:** {selected_problem['과목']} | **학년:** {selected_problem['학년']} | **난이도:** {selected_problem['난이도']}")
                    st.markdown(f"### {selected_problem['문제내용']}")
                    
                    # 객관식 보기 표시
                    if selected_problem['문제유형'] == '객관식':
                        options = []
                        for i in range(1, 6):
                            option_key = f'보기{i}'
                            if pd.notna(selected_problem[option_key]) and selected_problem[option_key] != "":
                                st.write(f"{i}. {selected_problem[option_key]}")
                    
                    # 답안 입력
                    with st.form(f"submit_answer_{selected_problem['문제ID']}"):
                        if selected_problem['문제유형'] == '객관식':
                            user_answer = st.text_input("답변 (번호만 입력)", key=f"answer_{selected_problem['문제ID']}")
                        else:
                            user_answer = st.text_area("답변", key=f"answer_{selected_problem['문제ID']}")
                        
                        submit = st.form_submit_button("제출")
                        
                        if submit:
                            if user_answer:
                                # 답안 채점
                                score, feedback = grade_answer(
                                    selected_problem['문제유형'],
                                    selected_problem['정답'],
                                    user_answer,
                                    selected_problem['키워드']
                                )
                                
                                # 결과 표시
                                if score >= 80:
                                    st.success(f"점수: {score} - {feedback}")
                                elif score >= 50:
                                    st.warning(f"점수: {score} - {feedback}")
                                else:
                                    st.error(f"점수: {score} - {feedback}")
                                
                                # 해설 표시
                                with st.expander("해설 보기"):
                                    st.write(selected_problem['해설'])
                                
                                # 답안 저장
                                save_success = save_answer(
                                    st.session_state.user_data['username'],
                                    st.session_state.user_data['name'],
                                    st.session_state.user_data['grade'],
                                    selected_problem['문제ID'],
                                    user_answer,
                                    score,
                                    feedback
                                )
                                
                                if save_success:
                                    st.info("답안이 성공적으로 저장되었습니다.")
                                else:
                                    st.error("답안 저장 중 오류가 발생했습니다.")
                            else:
                                st.error("답변을 입력해주세요.")
            else:
                st.warning("조건에 맞는 문제가 없습니다.")
        else:
            st.error("문제를 불러올 수 없습니다.")
    
    with tab2:
        st.subheader("📊 내 성적")
        
        _, answers_df = load_data()
        
        if answers_df is not None and not answers_df.empty:
            # 현재 학생의 답안만 필터링
            student_answers = answers_df[answers_df['학생ID'] == st.session_state.user_data['username']]
            
            if not student_answers.empty:
                st.dataframe(student_answers)
                
                # 기본 통계 계산
                avg_score = student_answers['점수'].astype(float).mean()
                total_problems = len(student_answers)
                correct_problems = len(student_answers[student_answers['점수'].astype(float) >= 80])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("푼 문제 수", total_problems)
                with col2:
                    st.metric("평균 점수", f"{avg_score:.1f}")
                with col3:
                    st.metric("정답률", f"{correct_problems/total_problems*100:.1f}%" if total_problems > 0 else "0%")
                
                # 과목별 평균 계산을 위해 문제 데이터와 결합
                problems_df, _ = load_data()
                if problems_df is not None:
                    merged_data = pd.merge(student_answers, problems_df[['문제ID', '과목']], on='문제ID', how='left')
                    if not merged_data.empty:
                        subject_avg = merged_data.groupby('과목')['점수'].mean().reset_index()
                        
                        st.subheader("과목별 평균 점수")
                        for _, row in subject_avg.iterrows():
                            st.metric(row['과목'], f"{row['점수']:.1f}")
            else:
                st.info("제출한 답안이 없습니다.")
        else:
            st.error("성적 데이터를 불러올 수 없습니다.")

def main():
    # 데이터 초기화
    initialize_sample_data()
    
    # 사이드바 - 로그인 정보 및 로그아웃 버튼
    if st.session_state.authenticated:
        with st.sidebar:
            st.write(f"로그인: {st.session_state.user_data['name']} ({st.session_state.user_data['role']})")
            if st.button("로그아웃"):
                logout()
                st.rerun()

    # 현재 페이지에 따라 렌더링
    if st.session_state.page == "login":
        login_screen()
    elif st.session_state.page == "teacher" and st.session_state.authenticated:
        teacher_dashboard()
    elif st.session_state.page == "student" and st.session_state.authenticated:
        student_portal()
    else:
        st.session_state.page = "login"
        login_screen()

if __name__ == "__main__":
    main() 