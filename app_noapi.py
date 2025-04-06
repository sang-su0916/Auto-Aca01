import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# 페이지 설정
st.set_page_config(page_title="학원 자동 첨삭 시스템", page_icon="📚")

# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None
if "username" not in st.session_state:
    st.session_state.username = None
if "student_id" not in st.session_state:
    st.session_state.student_id = None
if "grade" not in st.session_state:
    st.session_state.grade = None

# 초기 데이터 로드 및 생성
def load_data():
    # 문제 데이터 생성
    if not os.path.exists("sample_questions.csv"):
        initial_problems = pd.DataFrame({
            '문제ID': ['P20250401001', 'P20250401002', 'P20250401003'],
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
    
    # 답안 데이터 생성
    if not os.path.exists("student_answers.csv"):
        initial_answers = pd.DataFrame({
            '학생ID': ['S001', 'S002'],
            '이름': ['홍길동', '김철수'],
            '학년': ['중3', '중2'],
            '문제ID': ['P20250401001', 'P20250401002'],
            '제출답안': ['2', '1'],
            '점수': [100, 100],
            '피드백': ['정답입니다!', '정답입니다!'],
            '제출시간': [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        initial_answers.to_csv("student_answers.csv", index=False, encoding='utf-8')
    
    # 데이터 로드
    try:
        problems = pd.read_csv("sample_questions.csv", encoding='utf-8')
        answers = pd.read_csv("student_answers.csv", encoding='utf-8')
        return problems, answers
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return None, None

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

# 로그인 페이지
def login_page():
    """로그인 페이지 표시"""
    st.markdown("<h1 style='text-align: center;'>📚 학원 자동 첨삭 시스템</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='background-color: #f0f2f6; padding: 2rem; border-radius: 10px;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>로그인</h2>", unsafe_allow_html=True)
        
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        
        # 데모 계정 정보
        with st.expander("데모 계정 정보"):
            st.markdown("""
            **교사 계정**
            - 아이디: teacher
            - 비밀번호: demo123
            
            **학생 계정**
            - 아이디: student
            - 비밀번호: demo123
            """)
        
        if st.button("로그인"):
            if username == "teacher" and password == "demo123":
                st.session_state.authenticated = True
                st.session_state.user_type = "teacher"
                st.session_state.username = "선생님"
                st.rerun()
            elif username == "student" and password == "demo123":
                st.session_state.authenticated = True
                st.session_state.user_type = "student"
                st.session_state.username = "홍길동"
                st.session_state.student_id = "S001"
                st.session_state.grade = "중3"
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# 교사 대시보드
def teacher_dashboard():
    """교사 대시보드 표시"""
    st.markdown(f"<h1 style='text-align: center;'>👨‍🏫 교사 대시보드 - {st.session_state.username}</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["문제 관리", "학생 성적"])
    
    with tab1:
        st.subheader("📝 문제 관리")
        problems_df, _ = load_data()
        
        if problems_df is not None and not problems_df.empty:
            st.dataframe(problems_df)
            st.success(f"총 {len(problems_df)}개의 문제가 등록되어 있습니다.")
        else:
            st.info("등록된 문제가 없습니다.")
        
        # 새 문제 추가 폼
        st.subheader("📚 새 문제 추가")
        with st.form("add_problem_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                problem_id = st.text_input("문제 ID", f"P{datetime.now().strftime('%Y%m%d%H%M%S')}")
                subject = st.selectbox("과목", ["영어", "수학", "국어", "과학", "사회"])
                grade = st.selectbox("학년", ["중1", "중2", "중3", "고1", "고2", "고3"])
            
            with col2:
                problem_type = st.selectbox("문제 유형", ["객관식", "주관식"])
                difficulty = st.selectbox("난이도", ["상", "중", "하"])
            
            problem_content = st.text_area("문제 내용", placeholder="문제를 입력하세요.")
            
            if problem_type == "객관식":
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
            
            answer = st.text_input("정답", placeholder="객관식은 번호, 주관식은 정답을 입력하세요.")
            keywords = st.text_input("키워드 (주관식용, 쉼표로 구분)", placeholder="예: 키워드1, 키워드2, 키워드3")
            explanation = st.text_area("해설", placeholder="문제에 대한 해설을 입력하세요.")
            
            submit = st.form_submit_button("문제 추가")
            
            if submit:
                if problem_id and subject and grade and problem_content and answer:
                    try:
                        # 기존 문제 데이터 로드
                        problems_df, _ = load_data()
                        
                        # 새 문제 데이터
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
                        st.error(f"문제 추가 중 오류가 발생했습니다: {e}")
                else:
                    st.error("필수 필드를 모두 입력해주세요.")
    
    with tab2:
        st.subheader("📊 학생 성적")
        _, answers_df = load_data()
        
        if answers_df is not None and not answers_df.empty:
            st.dataframe(answers_df)
            
            # 통계 계산
            if 'score' in answers_df:
                avg_score = answers_df['score'].mean()
                st.metric("평균 점수", f"{avg_score:.1f}점")
            
            # 학생별 성적
            if not answers_df.empty:
                student_scores = answers_df.groupby('이름')['점수'].mean().reset_index()
                st.subheader("학생별 평균 점수")
                for _, row in student_scores.iterrows():
                    st.metric(row['이름'], f"{row['점수']:.1f}점")
        else:
            st.info("제출된 답안이 없습니다.")

# 학생 포털
def student_portal():
    """학생 포털 페이지 표시"""
    st.markdown(f"<h1 style='text-align: center;'>👨‍🎓 학생 포털 - {st.session_state.username}</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["문제 풀기", "나의 성적"])
    
    with tab1:
        st.subheader("📝 문제 풀기")
        problems_df, _ = load_data()
        
        if problems_df is not None and not problems_df.empty:
            # 필터 옵션
            col1, col2, col3 = st.columns(3)
            with col1:
                subject_filter = st.selectbox("과목 선택", ["전체"] + problems_df['과목'].unique().tolist())
            with col2:
                grade_filter = st.selectbox("학년 선택", ["전체"] + problems_df['학년'].unique().tolist())
            with col3:
                difficulty_filter = st.selectbox("난이도 선택", ["전체"] + problems_df['난이도'].unique().tolist())
            
            # 필터 적용
            filtered_problems = problems_df.copy()
            if subject_filter != "전체":
                filtered_problems = filtered_problems[filtered_problems['과목'] == subject_filter]
            if grade_filter != "전체":
                filtered_problems = filtered_problems[filtered_problems['학년'] == grade_filter]
            if difficulty_filter != "전체":
                filtered_problems = filtered_problems[filtered_problems['난이도'] == difficulty_filter]
            
            # 문제 목록 표시
            if not filtered_problems.empty:
                st.write(f"총 {len(filtered_problems)}개의 문제가 있습니다.")
                
                # 문제 선택
                problem_ids = filtered_problems['문제ID'].tolist()
                problem_titles = [f"{row['문제ID']} - {row['과목']} ({row['학년']}, {row['난이도']})" for _, row in filtered_problems.iterrows()]
                selected_problem_index = st.selectbox("풀 문제 선택", range(len(problem_ids)), format_func=lambda i: problem_titles[i])
                
                if selected_problem_index is not None:
                    selected_problem = filtered_problems.iloc[selected_problem_index]
                    
                    # 문제 표시
                    st.markdown("---")
                    st.subheader(f"📝 문제: {selected_problem['문제ID']}")
                    st.write(f"**과목:** {selected_problem['과목']}")
                    st.write(f"**학년:** {selected_problem['학년']}")
                    st.write(f"**난이도:** {selected_problem['난이도']}")
                    st.markdown(f"### {selected_problem['문제내용']}")
                    
                    # 객관식 보기 표시
                    if selected_problem['문제유형'] == '객관식':
                        options = []
                        if not pd.isna(selected_problem['보기1']) and selected_problem['보기1']:
                            options.append(f"1. {selected_problem['보기1']}")
                        if not pd.isna(selected_problem['보기2']) and selected_problem['보기2']:
                            options.append(f"2. {selected_problem['보기2']}")
                        if not pd.isna(selected_problem['보기3']) and selected_problem['보기3']:
                            options.append(f"3. {selected_problem['보기3']}")
                        if not pd.isna(selected_problem['보기4']) and selected_problem['보기4']:
                            options.append(f"4. {selected_problem['보기4']}")
                        if not pd.isna(selected_problem['보기5']) and selected_problem['보기5']:
                            options.append(f"5. {selected_problem['보기5']}")
                        
                        for option in options:
                            st.markdown(option)
                    
                    # 답안 입력 폼
                    with st.form("answer_form"):
                        if selected_problem['문제유형'] == '객관식':
                            answer = st.text_input("답안 제출 (번호만 입력)", placeholder="예: 1, 2, 3, ...")
                        else:
                            answer = st.text_area("답안 제출", placeholder="답안을 입력하세요...")
                        
                        submit = st.form_submit_button("제출")
                        
                        if submit:
                            if answer:
                                # 채점
                                score, feedback = grade_answer(
                                    selected_problem['문제유형'],
                                    selected_problem['정답'],
                                    answer,
                                    selected_problem['키워드'] if '키워드' in selected_problem else None
                                )
                                
                                # 결과 표시
                                if score >= 80:
                                    st.success(f"점수: {score}점 - {feedback}")
                                elif score >= 50:
                                    st.warning(f"점수: {score}점 - {feedback}")
                                else:
                                    st.error(f"점수: {score}점 - {feedback}")
                                
                                # 해설 표시
                                with st.expander("해설 보기"):
                                    st.write(selected_problem['해설'])
                                
                                # 답안 저장
                                save_success = save_answer(
                                    st.session_state.student_id,
                                    st.session_state.username,
                                    st.session_state.grade,
                                    selected_problem['문제ID'],
                                    answer,
                                    score,
                                    feedback
                                )
                                
                                if save_success:
                                    st.info("답안이 저장되었습니다.")
                                else:
                                    st.error("답안 저장 중 오류가 발생했습니다.")
                            else:
                                st.error("답안을 입력해주세요.")
            else:
                st.info("선택한 조건에 맞는 문제가 없습니다.")
        else:
            st.info("등록된 문제가 없습니다.")
    
    with tab2:
        st.subheader("📊 나의 성적")
        _, answers_df = load_data()
        
        if answers_df is not None and not answers_df.empty:
            # 현재 학생의 답안만 필터링
            student_answers = answers_df[answers_df['학생ID'] == st.session_state.student_id]
            
            if not student_answers.empty:
                st.dataframe(student_answers)
                
                # 통계
                avg_score = student_answers['점수'].astype(float).mean()
                st.metric("평균 점수", f"{avg_score:.1f}점")
                
                # 과목별 성적 (문제 데이터와 조인 필요)
                problems_df, _ = load_data()
                if problems_df is not None:
                    merged_data = pd.merge(
                        student_answers,
                        problems_df[['문제ID', '과목']],
                        on='문제ID',
                        how='left'
                    )
                    
                    subject_scores = merged_data.groupby('과목')['점수'].mean().reset_index()
                    
                    if not subject_scores.empty:
                        st.subheader("과목별 평균 점수")
                        for _, row in subject_scores.iterrows():
                            st.metric(row['과목'], f"{row['점수']:.1f}점")
            else:
                st.info("제출한 답안이 없습니다.")
        else:
            st.info("제출한 답안이 없습니다.")

# 메인 함수
def main():
    """메인 함수"""
    # 초기 데이터 로드
    load_data()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        # 사이드바
        st.sidebar.title("메뉴")
        
        if st.sidebar.button("로그아웃"):
            st.session_state.authenticated = False
            st.session_state.user_type = None
            st.session_state.username = None
            st.session_state.student_id = None
            st.session_state.grade = None
            st.rerun()
        
        # 페이지 표시
        if st.session_state.user_type == "teacher":
            teacher_dashboard()
        else:
            student_portal()

# 앱 실행
if __name__ == "__main__":
    main() 