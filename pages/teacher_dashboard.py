import streamlit as st
import pandas as pd
from datetime import datetime

def render_problem_upload():
    """Render problem upload form"""
    with st.form("problem_upload_form"):
        problem_text = st.text_area("문제 내용", height=200)
        
        col1, col2 = st.columns(2)
        with col1:
            difficulty = st.selectbox(
                "난이도",
                ["쉬움", "보통", "어려움"]
            )
        
        with col2:
            keywords = st.text_input(
                "키워드 (쉼표로 구분)",
                placeholder="예: 문법, 어휘, 독해"
            )
        
        model_answer = st.text_area("모범답안", height=150)
        
        submitted = st.form_submit_button("문제 등록")
        
        if submitted and problem_text and model_answer:
            # Generate problem ID (timestamp-based)
            problem_id = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Prepare data for sheets
            problem_data = [
                [
                    problem_id,
                    problem_text,
                    difficulty,
                    model_answer,
                    keywords
                ]
            ]
            
            try:
                # Get sheets API from session state
                sheets_api = st.session_state.sheets_api
                sheets_api.append_row(
                    st.secrets["spreadsheet_id"],
                    "problems",
                    problem_data[0]
                )
                st.success("문제가 성공적으로 등록되었습니다!")
                
            except Exception as e:
                st.error(f"문제 등록 중 오류가 발생했습니다: {str(e)}")
        
        elif submitted:
            st.warning("모든 필수 항목을 입력해주세요.")

def render_statistics():
    """Render grade statistics"""
    try:
        # Get sheets API from session state
        sheets_api = st.session_state.sheets_api
        
        # Read student answers data
        data = sheets_api.read_range(
            st.secrets["spreadsheet_id"],
            "student_answers"
        )
        
        if len(data) > 1:  # If there's data beyond headers
            df = pd.DataFrame(data[1:], columns=data[0])
            
            st.subheader("전체 성적 분포")
            scores = pd.to_numeric(df['점수'], errors='coerce')
            st.bar_chart(scores.value_counts().sort_index())
            
            st.subheader("학생별 성적 현황")
            student_avg = df.groupby('이름')['점수'].agg(['mean', 'count']).round(2)
            st.dataframe(student_avg)
            
            st.subheader("문제별 정답률")
            problem_stats = df.groupby('문제ID')['점수'].agg(['mean', 'count']).round(2)
            st.dataframe(problem_stats)
            
        else:
            st.info("아직 제출된 답안이 없습니다.")
            
    except Exception as e:
        st.error(f"통계 데이터를 불러오는 중 오류가 발생했습니다: {str(e)}") 