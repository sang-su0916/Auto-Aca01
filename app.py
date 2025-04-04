import streamlit as st
import os
import pandas as pd
import base64
from datetime import datetime

# 환경 변수 설정 (Streamlit Cloud 배포용)
from sheets.setup_env import setup_credentials, get_spreadsheet_id
setup_credentials()

# Google Sheets API 사용 여부 설정
USE_GOOGLE_SHEETS = True

# Google Sheets API가 사용 가능한 경우 모듈 임포트 시도
if USE_GOOGLE_SHEETS:
    try:
        from sheets.google_sheets import GoogleSheetsAPI
        sheets_api = GoogleSheetsAPI()
        SHEETS_AVAILABLE = True
    except ImportError as e:
        st.error(f"Google Sheets API 연결 오류: {str(e)}")
        SHEETS_AVAILABLE = False
else:
    SHEETS_AVAILABLE = False

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'show_sidebar' not in st.session_state:
    st.session_state.show_sidebar = False

# Hide sidebar by default
st.set_page_config(initial_sidebar_state="collapsed")

def get_csv_download_link():
    """샘플 CSV 파일 다운로드 링크 생성"""
    with open('sample_problems.csv', 'r', encoding='utf-8') as f:
        csv = f.read()
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="sample_problems.csv">📥 샘플 CSV 파일 다운로드</a>'
    return href

# Custom CSS to improve UI
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    /* Hide sidebar toggle by default */
    .css-1rs6os {
        visibility: hidden;
    }
    .css-1dp5vir {
        visibility: hidden;
    }
    .download-link {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .csv-guide {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def teacher_dashboard():
    st.title("👨‍🏫 교사 대시보드")
    st.write("문제 관리 및 학생 성적 확인")
    
    tab1, tab2 = st.tabs(["문제 관리", "성적 통계"])
    
    with tab1:
        st.subheader("📝 문제 관리")
        
        # 기존 문제 표시
        if SHEETS_AVAILABLE:
            problems = sheets_api.get_problems()
            if problems:
                st.subheader("등록된 문제 목록")
                problems_df = pd.DataFrame(problems)
                st.dataframe(problems_df)
                st.success(f"총 {len(problems)}개의 문제가 등록되어 있습니다.")
            else:
                st.info("현재 등록된 문제가 없습니다.")
        
        st.subheader("📝 새 문제 업로드")
        
        # CSV 가이드
        st.markdown("""
        <div class='csv-guide'>
        <h4>📋 CSV 파일 작성 가이드</h4>
        <p>다음 형식에 맞춰 CSV 파일을 작성해주세요:</p>
        <ul>
            <li>문제ID: 고유한 숫자</li>
            <li>과목: 수학, 영어, 국어 등</li>
            <li>학년: 중1, 중2, 중3, 고1, 고2, 고3</li>
            <li>문제유형: 객관식, 주관식, 서술형</li>
            <li>난이도: 상, 중, 하</li>
            <li>문제내용: 실제 문제 내용</li>
            <li>보기1~5: 객관식인 경우 보기 내용</li>
            <li>정답: 정답 또는 모범답안</li>
            <li>키워드: 채점 키워드(쉼표로 구분)</li>
            <li>해설: 문제 해설</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 샘플 CSV 다운로드 링크
        st.markdown("<div class='download-link'>", unsafe_allow_html=True)
        st.markdown(get_csv_download_link(), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 파일 업로드
        uploaded_file = st.file_uploader("CSV 파일 선택", type=['csv'])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success("파일이 성공적으로 업로드되었습니다!")
                
                # 업로드된 문제 미리보기
                st.subheader("📊 업로드된 문제 미리보기")
                st.dataframe(df)
                
                # 통계 정보
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("총 문제 수", len(df))
                with col2:
                    st.metric("문제 유형 수", len(df['문제유형'].unique()))
                with col3:
                    st.metric("과목 수", len(df['과목'].unique()))
                
                # Google Sheets에 저장 버튼
                if st.button("Google Sheets에 저장"):
                    if SHEETS_AVAILABLE:
                        # CSV 데이터를 Google Sheets 형식으로 변환
                        values = df.values.tolist()
                        # 첫 번째 행이 헤더인 경우 제거
                        if list(df.columns) == ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                                            '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']:
                            pass
                        else:
                            # 헤더 행 추가
                            values.insert(0, list(df.columns))
                        
                        # Google Sheets에 저장
                        try:
                            sheets_api.write_range('problems!A2:N100', values)
                            st.success("문제가 Google Sheets에 성공적으로 저장되었습니다!")
                        except Exception as e:
                            st.error(f"Google Sheets 저장 중 오류가 발생했습니다: {str(e)}")
                    else:
                        st.error("Google Sheets API를 사용할 수 없습니다.")
                
            except Exception as e:
                st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
        
        # 수동 문제 추가
        st.subheader("📝 문제 직접 추가")
        with st.form("add_problem_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                problem_id = st.text_input("문제ID", value=f"P{str(len(sheets_api.get_problems()) + 1).zfill(3)}")
                subject = st.selectbox("과목", ["영어", "수학", "국어", "과학", "사회"])
            with col2:
                grade = st.selectbox("학년", ["중1", "중2", "중3", "고1", "고2", "고3"])
                problem_type = st.selectbox("문제유형", ["객관식", "주관식", "서술형"])
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
                    new_problem = [
                        problem_id, subject, grade, problem_type, difficulty, problem_content,
                        option1, option2, option3, option4, option5, answer, keywords, explanation
                    ]
                    
                    if SHEETS_AVAILABLE:
                        try:
                            # 마지막 행 다음에 추가
                            problems = sheets_api.get_problems()
                            next_row = len(problems) + 2  # 헤더(1) + 기존 문제 수 + 1
                            sheets_api.write_range(f'problems!A{next_row}:N{next_row}', [new_problem])
                            st.success("문제가 성공적으로 추가되었습니다!")
                        except Exception as e:
                            st.error(f"문제 추가 중 오류가 발생했습니다: {str(e)}")
                    else:
                        st.error("Google Sheets API를 사용할 수 없습니다.")
                else:
                    st.error("필수 필드(문제ID, 과목, 학년, 문제 내용, 정답)를 모두 입력해주세요.")
    
    with tab2:
        st.subheader("📈 성적 통계")
        
        if SHEETS_AVAILABLE:
            # 학생 답안 데이터 가져오기
            try:
                student_answers = sheets_api.read_range('student_answers!A2:H')
                if student_answers:
                    answers_df = pd.DataFrame(student_answers, columns=[
                        '학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간'
                    ])
                    st.dataframe(answers_df)
                    
                    # 통계 정보
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("총 제출 답안 수", len(answers_df))
                    with col2:
                        st.metric("학생 수", len(answers_df['학생ID'].unique()))
                    with col3:
                        # 점수가 비어있지 않은 경우에만 평균 계산
                        valid_scores = answers_df[answers_df['점수'] != '']['점수']
                        if not valid_scores.empty:
                            avg_score = sum(map(float, valid_scores)) / len(valid_scores)
                            st.metric("평균 점수", f"{avg_score:.1f}")
                        else:
                            st.metric("평균 점수", "N/A")
                else:
                    st.info("아직 제출된 답안이 없습니다.")
            except Exception as e:
                st.error(f"데이터 로딩 중 오류가 발생했습니다: {str(e)}")
        else:
            st.error("Google Sheets API를 사용할 수 없어 성적 통계를 확인할 수 없습니다.")

def student_portal():
    st.title("👨‍🎓 학생 포털")
    st.write("문제 풀기 및 성적 확인")
    
    tab1, tab2 = st.tabs(["문제 풀기", "성적 확인"])
    
    with tab1:
        st.subheader("문제 목록")
        
        if SHEETS_AVAILABLE:
            problems = sheets_api.get_problems()
            
            if not problems:
                st.info("현재 등록된 문제가 없습니다.")
            else:
                # 필터링 옵션
                col1, col2, col3 = st.columns(3)
                with col1:
                    grade_filter = st.selectbox("학년 필터", ["전체"] + list(set(p['학년'] for p in problems)))
                with col2:
                    subject_filter = st.selectbox("과목 필터", ["전체"] + list(set(p['과목'] for p in problems)))
                with col3:
                    difficulty_filter = st.selectbox("난이도 필터", ["전체"] + list(set(p['난이도'] for p in problems)))
                
                # 필터링 적용
                filtered_problems = problems
                if grade_filter != "전체":
                    filtered_problems = [p for p in filtered_problems if p['학년'] == grade_filter]
                if subject_filter != "전체":
                    filtered_problems = [p for p in filtered_problems if p['과목'] == subject_filter]
                if difficulty_filter != "전체":
                    filtered_problems = [p for p in filtered_problems if p['난이도'] == difficulty_filter]
                
                if not filtered_problems:
                    st.info("선택한 조건에 맞는 문제가 없습니다.")
                else:
                    st.success(f"총 {len(filtered_problems)}개의 문제가 있습니다.")
                    
                    # 문제 목록 표시
                    for problem in filtered_problems:
                        with st.expander(f"문제 {problem['문제ID']}: {problem['문제내용'][:50]}..."):
                            st.write(f"**과목:** {problem['과목']}")
                            st.write(f"**학년:** {problem['학년']}")
                            st.write(f"**유형:** {problem['문제유형']}")
                            st.write(f"**난이도:** {problem['난이도']}")
                            st.write(f"**문제 내용:**\n{problem['문제내용']}")
                            
                            # 객관식 문제인 경우 보기 표시
                            if problem['문제유형'] == '객관식':
                                option_cols = st.columns(2)
                                for i in range(1, 6):
                                    option_key = f'보기{i}'
                                    if option_key in problem and problem[option_key]:
                                        with option_cols[i % 2]:
                                            st.write(f"**보기 {i}:** {problem[option_key]}")
                            
                            # 제출 폼
                            with st.form(f"answer_form_{problem['문제ID']}"):
                                if problem['문제유형'] == '객관식':
                                    options = []
                                    for i in range(1, 6):
                                        option_key = f'보기{i}'
                                        if option_key in problem and problem[option_key]:
                                            options.append(problem[option_key])
                                    answer = st.radio("답안 선택:", options, key=f"radio_{problem['문제ID']}")
                                else:
                                    answer = st.text_area("답안 작성", key=f"textarea_{problem['문제ID']}")
                                
                                if st.form_submit_button("제출"):
                                    if answer:
                                        # 답안 제출 처리
                                        try:
                                            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            
                                            # 정답 비교
                                            correct_answer = problem['정답']
                                            score = "100" if answer == correct_answer else "0"
                                            feedback = "정답입니다!" if score == "100" else f"오답입니다. 정답은 '{correct_answer}'입니다."
                                            
                                            student_data = [
                                                st.session_state.student_id,
                                                st.session_state.name,
                                                st.session_state.grade,
                                                problem['문제ID'],
                                                answer,
                                                score,
                                                feedback,
                                                now
                                            ]
                                            
                                            # Google Sheets에 저장
                                            sheets_api.append_row('student_answers', student_data)
                                            
                                            if score == "100":
                                                st.success(f"정답입니다! 점수: {score}")
                                            else:
                                                st.error(f"오답입니다. 정답은 '{correct_answer}'입니다. 점수: {score}")
                                                st.info(f"**해설:** {problem['해설']}")
                                        except Exception as e:
                                            st.error(f"답안 제출 중 오류가 발생했습니다: {str(e)}")
                                    else:
                                        st.error("답안을 입력해주세요.")
        else:
            st.error("Google Sheets API를 사용할 수 없어 문제를 가져올 수 없습니다.")
    
    with tab2:
        st.subheader("나의 성적")
        
        if SHEETS_AVAILABLE:
            try:
                # 학생 답안 데이터 가져오기
                student_answers = sheets_api.read_range('student_answers!A2:H')
                if student_answers:
                    # 현재 로그인한 학생의 답안만 필터링
                    my_answers = []
                    for answer in student_answers:
                        if len(answer) > 0 and answer[0] == st.session_state.student_id:
                            my_answers.append({
                                '문제ID': answer[3],
                                '제출답안': answer[4],
                                '점수': answer[5],
                                '피드백': answer[6],
                                '제출시간': answer[7] if len(answer) > 7 else ''
                            })
                    
                    if my_answers:
                        # 성적 통계
                        valid_scores = [int(a['점수']) for a in my_answers if a['점수']]
                        if valid_scores:
                            avg_score = sum(valid_scores) / len(valid_scores)
                            correct_count = sum(1 for s in valid_scores if s == 100)
                            correct_rate = (correct_count / len(valid_scores)) * 100
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("평균 점수", f"{avg_score:.1f}")
                            with col2:
                                st.metric("정답률", f"{correct_rate:.1f}%")
                            with col3:
                                st.metric("총 제출 답안 수", len(my_answers))
                        
                        # 답안 목록
                        st.subheader("제출한 답안 목록")
                        for answer in my_answers:
                            with st.expander(f"문제 {answer['문제ID']} ({answer['제출시간']})"):
                                # 문제 내용 찾기
                                problem_content = "문제 내용을 찾을 수 없습니다."
                                problems = sheets_api.get_problems()
                                for p in problems:
                                    if p['문제ID'] == answer['문제ID']:
                                        problem_content = p['문제내용']
                                        break
                                
                                st.write(f"**문제 내용:** {problem_content}")
                                st.write(f"**제출 답안:** {answer['제출답안']}")
                                st.write(f"**점수:** {answer['점수']}")
                                st.write(f"**피드백:** {answer['피드백']}")
                    else:
                        st.info("아직 제출한 답안이 없습니다.")
                else:
                    st.info("아직 제출한 답안이 없습니다.")
            except Exception as e:
                st.error(f"성적 데이터 로딩 중 오류가 발생했습니다: {str(e)}")
        else:
            st.error("Google Sheets API를 사용할 수 없어 성적을 확인할 수 없습니다.")

def login():
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>📚 학원 자동 첨삭 시스템</h1>", unsafe_allow_html=True)
    
    # Create columns for centering the login form
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 2rem; border-radius: 10px;'>
            <h2 style='text-align: center; margin-bottom: 2rem;'>로그인</h2>
        """, unsafe_allow_html=True)
        
        username = st.text_input("아이디", key="username")
        password = st.text_input("비밀번호", type="password", key="password")
        
        # Show demo credentials with toggle
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
            if username == "teacher" and password == "demo1234":
                st.session_state.authenticated = True
                st.session_state.user_type = "teacher"
                st.session_state.show_sidebar = True
                st.rerun()
            elif username == "student" and password == "demo5678":
                st.session_state.authenticated = True
                st.session_state.user_type = "student"
                st.session_state.show_sidebar = True
                st.session_state.student_id = "S001"
                st.session_state.name = "홍길동"
                st.session_state.grade = "중3"
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")
        
        st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main application function"""
    if not st.session_state.authenticated:
        login()
    else:
        # Show sidebar for navigation
        st.sidebar.title("메뉴")
        
        # Available pages based on user type
        if st.session_state.user_type == "teacher":
            teacher_dashboard()
        else:
            student_portal()
        
        if st.sidebar.button("로그아웃"):
            st.session_state.authenticated = False
            st.session_state.show_sidebar = False
            st.rerun()

if __name__ == "__main__":
    main() 