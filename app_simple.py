import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="학원 자동 첨삭 시스템", page_icon="📚")

def init_session_state():
    """세션 상태 초기화"""
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

def login_page():
    """로그인 페이지"""
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

def teacher_dashboard():
    """교사 대시보드"""
    st.title(f"👨‍🏫 {st.session_state.user_name} 대시보드")
    
    tab1, tab2 = st.tabs(["문제 관리", "성적 통계"])
    
    with tab1:
        st.subheader("📝 문제 업로드")
        st.info("Google Sheets API 연결 후 문제를 업로드할 수 있습니다.")
        
        # 예시 데이터
        df = pd.DataFrame({
            '문제ID': ['P001', 'P002', 'P003'],
            '과목': ['영어', '영어', '영어'],
            '학년': ['중3', '중3', '중3'],
            '문제유형': ['객관식', '주관식', '객관식'],
            '난이도': ['중', '상', '하'],
            '문제내용': ['What is the capital of the UK?', 'Write a sentence using the word "beautiful".', 'Which word is a verb?']
        })
        
        st.dataframe(df)
    
    with tab2:
        st.subheader("📊 성적 통계")
        st.info("Google Sheets API 연결 후 학생들의 성적을 확인할 수 있습니다.")
        
        # 예시 차트
        chart_data = pd.DataFrame({
            '학생': ['김민준', '이지우', '박서연', '최준호'],
            '점수': [85, 92, 78, 95]
        })
        
        st.bar_chart(chart_data.set_index('학생'))

def student_portal():
    """학생 포털"""
    st.title(f"👨‍🎓 {st.session_state.user_name} 포털")
    st.write(f"학년: {st.session_state.grade}, 학번: {st.session_state.user_id}")
    
    tab1, tab2 = st.tabs(["문제 풀기", "성적 확인"])
    
    with tab1:
        st.subheader("📝 문제 목록")
        st.info("Google Sheets API 연결 후 문제 목록을 볼 수 있습니다.")
        
        # 예시 문제
        with st.expander("문제 P001: What is the capital of the UK?"):
            st.write("**학년:** 중3")
            st.write("**과목:** 영어")
            st.write("**난이도:** 중")
            st.write("**보기 1:** London")
            st.write("**보기 2:** Paris")
            st.write("**보기 3:** Berlin")
            st.write("**보기 4:** Rome")
            
            answer = st.radio("정답 선택:", ["London", "Paris", "Berlin", "Rome"], key="q1")
            
            if st.button("제출", key="submit1"):
                if answer == "London":
                    st.success("정답입니다!")
                else:
                    st.error("오답입니다. 정답은 London입니다.")
    
    with tab2:
        st.subheader("📊 성적 현황")
        st.info("Google Sheets API 연결 후 성적을 확인할 수 있습니다.")
        
        # 예시 데이터
        results_data = pd.DataFrame({
            '문제ID': ['P001', 'P002', 'P003'],
            '제출답안': ['London', 'The sky is beautiful today.', 'run'],
            '점수': [100, 90, 100],
            '제출시간': ['2025-04-04 10:30:00', '2025-04-04 10:35:00', '2025-04-04 10:40:00']
        })
        
        st.dataframe(results_data)
        
        st.metric("평균 점수", "96.7점")

def main():
    """메인 함수"""
    # 세션 상태 초기화
    init_session_state()
    
    # 기능 구현
    if not st.session_state.authenticated:
        login_page()
    else:
        if st.session_state.user_type == "teacher":
            teacher_dashboard()
        else:
            student_portal()
        
        # 로그아웃 버튼
        if st.sidebar.button("로그아웃"):
            st.session_state.authenticated = False
            st.rerun()

if __name__ == "__main__":
    main() 