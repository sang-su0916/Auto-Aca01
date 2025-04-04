import streamlit as st
import pandas as pd
from datetime import datetime
from logic.grader import AutoGrader

def student_login():
    """Handle student login"""
    with st.form("login_form"):
        name = st.text_input("이름")
        student_id = st.text_input("학번")
        submitted = st.form_submit_button("로그인")
        
        if submitted and name and student_id:
            # Store student info in session state
            st.session_state.student_name = name
            st.session_state.student_id = student_id
            return True
    return False

def load_problems():
    """Load available problems from Google Sheets"""
    try:
        sheets_api = st.session_state.sheets_api
        data = sheets_api.read_range(
            st.secrets["spreadsheet_id"],
            "problems"
        )
        
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"문제를 불러오는 중 오류가 발생했습니다: {str(e)}")
        return pd.DataFrame()

def submit_answer(problem_id: str, answer: str, model_answer: str, keywords: str):
    """Submit and grade student's answer"""
    try:
        # Grade the answer
        grader = AutoGrader()
        score, feedback = grader.grade_answer(answer, model_answer, keywords)
        
        # Prepare submission data
        submission_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            st.session_state.student_name,
            st.session_state.student_id,
            problem_id,
            answer,
            str(score),
            feedback
        ]
        
        # Submit to Google Sheets
        sheets_api = st.session_state.sheets_api
        sheets_api.append_row(
            st.secrets["spreadsheet_id"],
            "student_answers",
            submission_data
        )
        
        return True, score, feedback
    except Exception as e:
        st.error(f"답안 제출 중 오류가 발생했습니다: {str(e)}")
        return False, None, None

def render_student_portal():
    """Render student portal page"""
    if 'student_name' not in st.session_state:
        if student_login():
            st.experimental_rerun()
    else:
        st.write(f"👋 안녕하세요, {st.session_state.student_name}님!")
        
        # Load and display problems
        problems_df = load_problems()
        
        if not problems_df.empty:
            st.subheader("📝 문제 목록")
            
            # Problem selection
            selected_difficulty = st.selectbox(
                "난이도 선택",
                ["전체"] + list(problems_df['난이도'].unique())
            )
            
            # Filter problems by difficulty
            if selected_difficulty != "전체":
                filtered_df = problems_df[problems_df['난이도'] == selected_difficulty]
            else:
                filtered_df = problems_df
            
            # Display problems
            for _, row in filtered_df.iterrows():
                with st.expander(f"문제 {row['문제ID']} ({row['난이도']})"):
                    st.write(row['문제'])
                    
                    # Answer submission form
                    with st.form(f"answer_form_{row['문제ID']}"):
                        answer = st.text_area("답안 작성", height=150)
                        submitted = st.form_submit_button("제출")
                        
                        if submitted and answer:
                            success, score, feedback = submit_answer(
                                row['문제ID'],
                                answer,
                                row['모범답안'],
                                row['키워드']
                            )
                            if success:
                                st.success("답안이 성공적으로 제출되었습니다!")
                                st.write(f"점수: {score}점")
                                st.write("피드백:")
                                st.write(feedback)
                        elif submitted:
                            st.warning("답안을 작성해주세요.") 