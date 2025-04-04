import streamlit as st
import pandas as pd
from datetime import datetime
import os
import random

# 페이지 설정
st.set_page_config(page_title="학원 자동 첨삭 시스템", page_icon="📚")

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

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'user_type' not in st.session_state:
    st.session_state.user_type = None

if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

if 'user_id' not in st.session_state:
    st.session_state.user_id = ""

if 'grade' not in st.session_state:
    st.session_state.grade = ""

# 로그인 함수
def login():
    st.markdown("<h1 style='text-align: center;'>📚 학원 자동 첨삭 시스템</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 2rem; border-radius: 10px;'>
            <h2 style='text-align: center; margin-bottom: 2rem;'>로그인</h2>
        """, unsafe_allow_html=True)
        
        username = st.text_input("아이디", key="username")
        password = st.text_input("비밀번호", type="password", key="password")
        
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
            if (username == "teacher" and password == "demo1234"):
                st.session_state.authenticated = True
                st.session_state.user_type = "teacher"
                st.session_state.user_name = "선생님"
                st.success("교사로 로그인되었습니다!")
                st.rerun()
            elif (username == "student" and password == "demo5678"):
                st.session_state.authenticated = True
                st.session_state.user_type = "student"
                st.session_state.user_name = "학생"
                st.session_state.user_id = "S001"
                st.session_state.grade = "중3"
                st.success("학생으로 로그인되었습니다!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# 교사 대시보드
def teacher_dashboard():
    st.title(f"👨‍🏫 {st.session_state.user_name} 대시보드")
    
    tab1, tab2 = st.tabs(["문제 관리", "성적 통계"])
    
    with tab1:
        st.subheader("📝 문제 목록")
        
        # 문제 목록 표시
        problems_df = pd.DataFrame(st.session_state.problems)
        st.dataframe(problems_df)
        
        # 문제 추가 폼
        st.subheader("➕ 새 문제 추가")
        with st.form("add_problem_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                subject = st.selectbox("과목", ["영어", "수학", "국어"])
                problem_id = f"P{str(len(st.session_state.problems) + 1).zfill(3)}"
            with col2:
                grade = st.selectbox("학년", ["중1", "중2", "중3", "고1", "고2", "고3"])
                problem_type = st.selectbox("문제유형", ["객관식", "주관식"])
            with col3:
                difficulty = st.selectbox("난이도", ["상", "중", "하"])
            
            problem_content = st.text_area("문제 내용")
            
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
            
            correct_answer = st.text_input("정답")
            keywords = st.text_input("키워드 (쉼표로 구분)")
            explanation = st.text_area("해설")
            
            if st.form_submit_button("문제 추가"):
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
                st.session_state.problems.append(new_problem)
                st.success(f"문제 {problem_id}가 추가되었습니다!")
                st.rerun()
    
    with tab2:
        st.subheader("📊 성적 통계")
        
        if not st.session_state.student_answers:
            st.info("아직 제출된 답안이 없습니다.")
        else:
            # 답안 목록
            answers_df = pd.DataFrame(st.session_state.student_answers)
            st.dataframe(answers_df)
            
            # 통계 카드
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_score = sum([ans['점수'] for ans in st.session_state.student_answers]) / len(st.session_state.student_answers)
                st.metric("평균 점수", f"{avg_score:.1f}점")
            with col2:
                correct_count = sum([1 for ans in st.session_state.student_answers if ans['점수'] == 100])
                correct_rate = (correct_count / len(st.session_state.student_answers)) * 100
                st.metric("정답률", f"{correct_rate:.1f}%")
            with col3:
                st.metric("총 제출 답안 수", len(st.session_state.student_answers))

# 학생 포털
def student_portal():
    st.title(f"👨‍🎓 {st.session_state.user_name} 포털")
    st.write(f"학년: {st.session_state.grade}, 학번: {st.session_state.user_id}")
    
    tab1, tab2 = st.tabs(["문제 풀기", "성적 확인"])
    
    with tab1:
        st.subheader("📝 문제 목록")
        
        # 필터링 옵션
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_subject = st.selectbox("과목 선택", ["전체"] + list(set([p['과목'] for p in st.session_state.problems])))
        with col2:
            filter_grade = st.selectbox("학년 선택", ["전체"] + list(set([p['학년'] for p in st.session_state.problems])))
        with col3:
            filter_difficulty = st.selectbox("난이도 선택", ["전체"] + list(set([p['난이도'] for p in st.session_state.problems])))
        
        # 필터링된 문제 목록
        filtered_problems = st.session_state.problems
        if filter_subject != "전체":
            filtered_problems = [p for p in filtered_problems if p['과목'] == filter_subject]
        if filter_grade != "전체":
            filtered_problems = [p for p in filtered_problems if p['학년'] == filter_grade]
        if filter_difficulty != "전체":
            filtered_problems = [p for p in filtered_problems if p['난이도'] == filter_difficulty]
        
        if not filtered_problems:
            st.info("선택한 조건에 맞는 문제가 없습니다.")
        else:
            # 문제 목록 표시
            for problem in filtered_problems:
                with st.expander(f"문제 {problem['문제ID']}: {problem['문제내용'][:50]}..."):
                    st.write(f"**과목:** {problem['과목']}")
                    st.write(f"**학년:** {problem['학년']}")
                    st.write(f"**유형:** {problem['문제유형']}")
                    st.write(f"**난이도:** {problem['난이도']}")
                    st.write(f"**문제 내용:**\n{problem['문제내용']}")
                    
                    # 보기 표시 (객관식인 경우)
                    if problem['문제유형'] == "객관식":
                        options = []
                        if problem['보기1']: options.append(problem['보기1'])
                        if problem['보기2']: options.append(problem['보기2'])
                        if problem['보기3']: options.append(problem['보기3'])
                        if problem['보기4']: options.append(problem['보기4'])
                        if problem['보기5']: options.append(problem['보기5'])
                        
                        answer = st.radio("정답 선택:", options, key=f"radio_{problem['문제ID']}")
                    else:
                        answer = st.text_area("답안 작성:", key=f"textarea_{problem['문제ID']}")
                    
                    if st.button("제출", key=f"submit_{problem['문제ID']}"):
                        if not answer:
                            st.error("답안을 입력해주세요.")
                        else:
                            # 점수 계산
                            score = 100 if answer == problem['정답'] else 0
                            feedback = "정답입니다!" if score == 100 else f"오답입니다. 정답은 {problem['정답']}입니다."
                            
                            # 답안 저장
                            submission = {
                                '학생ID': st.session_state.user_id,
                                '이름': st.session_state.user_name,
                                '학년': st.session_state.grade,
                                '문제ID': problem['문제ID'],
                                '제출답안': answer,
                                '점수': score,
                                '피드백': feedback,
                                '제출시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            st.session_state.student_answers.append(submission)
                            
                            if score == 100:
                                st.success(feedback)
                            else:
                                st.error(feedback)
                                st.info(f"**해설:** {problem['해설']}")
    
    with tab2:
        st.subheader("📊 성적 현황")
        
        # 내 답안 필터링
        my_answers = [ans for ans in st.session_state.student_answers if ans['학생ID'] == st.session_state.user_id]
        
        if not my_answers:
            st.info("아직 제출한 답안이 없습니다.")
        else:
            # 답안 목록
            my_answers_df = pd.DataFrame(my_answers)
            st.dataframe(my_answers_df)
            
            # 통계 카드
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_score = sum([ans['점수'] for ans in my_answers]) / len(my_answers)
                st.metric("평균 점수", f"{avg_score:.1f}점")
            with col2:
                correct_count = sum([1 for ans in my_answers if ans['점수'] == 100])
                correct_rate = (correct_count / len(my_answers)) * 100
                st.metric("정답률", f"{correct_rate:.1f}%")
            with col3:
                st.metric("총 제출 답안 수", len(my_answers))

# 메인 함수
def main():
    # 로그아웃 버튼 (로그인 상태일 때만 표시)
    if st.session_state.authenticated:
        if st.sidebar.button("로그아웃"):
            st.session_state.authenticated = False
            st.session_state.user_type = None
            st.session_state.user_name = ""
            st.session_state.user_id = ""
            st.session_state.grade = ""
            st.rerun()
    
    # 페이지 표시
    if not st.session_state.authenticated:
        login()
    else:
        if st.session_state.user_type == "teacher":
            teacher_dashboard()
        else:
            student_portal()

if __name__ == "__main__":
    main() 