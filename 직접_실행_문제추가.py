import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

# 초기 데이터 설정 (메모리에 저장)
problems = [
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

student_answers = []

# 앱 설정
st.set_page_config(
    page_title="학원 자동 첨삭 시스템",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'user_type' not in st.session_state:
    st.session_state.user_type = None

if 'problems' not in st.session_state:
    st.session_state.problems = problems

if 'student_answers' not in st.session_state:
    st.session_state.student_answers = student_answers

# CSS 스타일
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
    .problem-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #dfe1e5;
    }
</style>
""", unsafe_allow_html=True)

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

def load_csv_problems():
    """CSV 파일에서 문제 불러오기"""
    st.subheader("CSV 파일로 문제 추가")
    
    # 샘플 다운로드 기능
    sample_csv = """문제ID,과목,학년,문제유형,난이도,문제내용,보기1,보기2,보기3,보기4,보기5,정답,키워드,해설
P001,영어,중1,객관식,하,Which of the following is a fruit?,Apple,Book,Pencil,Chair,,Apple,"fruit,apple,vocabulary","Apple(사과)은 과일입니다. 나머지는 과일이 아닙니다."
P002,영어,중1,객관식,하,"Choose the correct subject pronoun: ___ is my friend.",He,Him,His,Himself,,He,"pronoun,subject pronoun,grammar","He는 주격 대명사입니다. Him(목적격), His(소유격), Himself(재귀대명사)는 주격 대명사가 아닙니다."
"""
    
    st.download_button(
        label="샘플 CSV 파일 다운로드",
        data=sample_csv,
        file_name="sample_questions.csv",
        mime="text/csv"
    )
    
    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # CSV 파일 읽기
            df = pd.read_csv(uploaded_file)
            
            # 필수 컬럼 확인
            required_columns = ["문제ID", "과목", "학년", "문제유형", "난이도", "문제내용", "정답", "키워드", "해설"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"다음 필수 컬럼이 CSV 파일에 없습니다: {', '.join(missing_columns)}")
                return False
            else:
                # 옵션 컬럼 확인 및 추가
                option_columns = ["보기1", "보기2", "보기3", "보기4", "보기5"]
                for col in option_columns:
                    if col not in df.columns:
                        df[col] = ""
                
                # 데이터 변환
                new_problems = []
                for _, row in df.iterrows():
                    problem = {
                        '문제ID': row['문제ID'],
                        '과목': row['과목'],
                        '학년': row['학년'],
                        '문제유형': row['문제유형'],
                        '난이도': row['난이도'],
                        '문제내용': row['문제내용'],
                        '보기1': row['보기1'],
                        '보기2': row['보기2'],
                        '보기3': row['보기3'],
                        '보기4': row['보기4'],
                        '보기5': row['보기5'],
                        '정답': row['정답'],
                        '키워드': row['키워드'],
                        '해설': row['해설']
                    }
                    new_problems.append(problem)
                
                # 기존 문제 목록과 병합할지 결정
                if st.session_state.problems:
                    merge_option = st.radio(
                        "기존 문제와 병합하시겠습니까?",
                        ["새 문제로 대체", "기존 문제에 추가"]
                    )
                    
                    if merge_option == "새 문제로 대체":
                        st.session_state.problems = new_problems
                        st.success(f"{len(new_problems)}개의 문제가 업로드되었습니다. 기존 문제는 제거되었습니다.")
                    else:
                        # 중복 문제ID 확인
                        existing_ids = {p['문제ID'] for p in st.session_state.problems}
                        add_problems = []
                        duplicate_ids = []
                        
                        for problem in new_problems:
                            if problem['문제ID'] in existing_ids:
                                duplicate_ids.append(problem['문제ID'])
                            else:
                                add_problems.append(problem)
                                existing_ids.add(problem['문제ID'])
                        
                        if duplicate_ids:
                            handle_duplicates = st.radio(
                                "중복된 문제ID가 있습니다. 어떻게 처리하시겠습니까?",
                                ["건너뛰기", "덮어쓰기"]
                            )
                            
                            if handle_duplicates == "덮어쓰기":
                                # 중복 제거
                                st.session_state.problems = [p for p in st.session_state.problems if p['문제ID'] not in [np['문제ID'] for np in new_problems]]
                                st.session_state.problems.extend(new_problems)
                                st.success(f"{len(new_problems)}개의 문제가 업로드되었습니다. {len(duplicate_ids)}개의 중복 문제가 덮어쓰기되었습니다.")
                            else:
                                st.session_state.problems.extend(add_problems)
                                st.success(f"{len(add_problems)}개의 새 문제가 추가되었습니다. {len(duplicate_ids)}개의 중복 문제는 건너뛰었습니다.")
                        else:
                            st.session_state.problems.extend(new_problems)
                            st.success(f"{len(new_problems)}개의 문제가 기존 목록에 추가되었습니다.")
                else:
                    st.session_state.problems = new_problems
                    st.success(f"{len(new_problems)}개의 문제가 업로드되었습니다.")
                
                # 미리보기
                st.subheader("업로드된 문제 미리보기")
                st.dataframe(df)
                return True
        
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
            return False
    
    return False

def teacher_dashboard():
    """교사 대시보드 표시"""
    st.title(f"👨‍🏫 {st.session_state.username}님의 대시보드")
    
    tab1, tab2, tab3 = st.tabs(["문제 관리", "학생 답안 확인", "CSV 문제 추가"])
    
    with tab1:
        st.subheader("📝 문제 목록")
        
        for i, problem in enumerate(st.session_state.problems):
            with st.expander(f"문제 {problem['문제ID']}: {problem['문제내용'][:30]}..."):
                cols = st.columns([1, 1, 1, 1])
                cols[0].write(f"**과목:** {problem['과목']}")
                cols[1].write(f"**학년:** {problem['학년']}")
                cols[2].write(f"**유형:** {problem['문제유형']}")
                cols[3].write(f"**난이도:** {problem['난이도']}")
                
                st.write(f"**문제 내용:** {problem['문제내용']}")
                
                if problem['문제유형'] == '객관식':
                    for j in range(1, 6):
                        if problem[f'보기{j}']:
                            st.write(f"**보기 {j}:** {problem[f'보기{j}']}")
                
                st.write(f"**정답:** {problem['정답']}")
                st.write(f"**키워드:** {problem['키워드']}")
                st.write(f"**해설:** {problem['해설']}")
                
                if st.button("삭제", key=f"delete_{i}"):
                    st.session_state.problems.pop(i)
                    st.rerun()
        
        st.subheader("➕ 새 문제 추가")
        with st.form("add_problem_form"):
            cols = st.columns([1, 1, 1, 1])
            problem_id = cols[0].text_input("문제ID (예: P004)")
            subject = cols[1].text_input("과목")
            grade = cols[2].text_input("학년")
            problem_type = cols[3].selectbox("문제유형", ["객관식", "주관식", "서술형"])
            
            difficulty = st.selectbox("난이도", ["상", "중", "하"])
            content = st.text_area("문제 내용")
            
            # 객관식인 경우 보기 표시
            options = [""] * 5
            if problem_type == "객관식":
                option_cols = st.columns(5)
                for i in range(5):
                    options[i] = option_cols[i].text_input(f"보기 {i+1}")
            
            answer = st.text_input("정답")
            keywords = st.text_input("키워드 (쉼표로 구분)")
            explanation = st.text_area("해설")
            
            if st.form_submit_button("문제 추가"):
                if problem_id and subject and grade and content and answer:
                    new_problem = {
                        '문제ID': problem_id,
                        '과목': subject,
                        '학년': grade,
                        '문제유형': problem_type,
                        '난이도': difficulty,
                        '문제내용': content,
                        '보기1': options[0],
                        '보기2': options[1],
                        '보기3': options[2],
                        '보기4': options[3],
                        '보기5': options[4],
                        '정답': answer,
                        '키워드': keywords,
                        '해설': explanation
                    }
                    st.session_state.problems.append(new_problem)
                    st.success("문제가 추가되었습니다!")
                    st.rerun()
                else:
                    st.error("필수 필드를 모두 입력해주세요.")
    
    with tab2:
        st.subheader("📊 학생 답안 목록")
        
        if not st.session_state.student_answers:
            st.info("학생 답안이 아직 없습니다.")
        else:
            for i, answer in enumerate(st.session_state.student_answers):
                with st.expander(f"제출: {answer[3]} - {answer[1]}"):
                    st.write(f"**학생ID:** {answer[0]}")
                    st.write(f"**이름:** {answer[1]}")
                    st.write(f"**학년:** {answer[2]}")
                    st.write(f"**문제ID:** {answer[3]}")
                    st.write(f"**제출답안:** {answer[4]}")
                    
                    # 문제 찾기
                    problem = None
                    for p in st.session_state.problems:
                        if p['문제ID'] == answer[3]:
                            problem = p
                            break
                    
                    if problem:
                        st.write(f"**실제 정답:** {problem['정답']}")
                        
                        # 점수와 피드백 입력
                        score = st.text_input("점수", value=answer[5], key=f"score_{i}")
                        feedback = st.text_area("피드백", value=answer[6], key=f"feedback_{i}")
                        
                        if st.button("저장", key=f"save_{i}"):
                            st.session_state.student_answers[i][5] = score
                            st.session_state.student_answers[i][6] = feedback
                            st.success("점수와 피드백이 저장되었습니다!")
                            st.rerun()
    
    with tab3:
        # CSV 문제 업로드 기능
        load_csv_problems()
        
        # CSV 파일 형식 안내
        with st.expander("CSV 파일 형식 안내"):
            st.markdown("""
            ### CSV 파일 형식
            
            CSV 파일은 다음 컬럼을 포함해야 합니다:
            
            - `문제ID`: 문제의 고유 식별자 (예: P001)
            - `과목`: 과목명 (예: 영어)
            - `학년`: 대상 학년 (예: 중3)
            - `문제유형`: 객관식, 주관식, 서술형 등
            - `난이도`: 상, 중, 하 중 하나
            - `문제내용`: 실제 문제 내용
            - `보기1` ~ `보기5`: 객관식 문제의 선택지 (선택 사항)
            - `정답`: 문제의 정답
            - `키워드`: 문제와 관련된 키워드 (쉼표로 구분)
            - `해설`: 문제 해설
            
            샘플 CSV 파일을 다운로드하여 형식을 확인하세요.
            """)
        
        # 문제 내보내기 기능
        if st.button("현재 문제 CSV로 내보내기"):
            if st.session_state.problems:
                df = pd.DataFrame(st.session_state.problems)
                csv_data = df.to_csv(index=False)
                
                st.download_button(
                    label="CSV 다운로드",
                    data=csv_data,
                    file_name="exported_problems.csv",
                    mime="text/csv",
                )
            else:
                st.warning("내보낼 문제가 없습니다.")

def student_portal():
    """학생 포털 표시"""
    st.title(f"👨‍🎓 {st.session_state.username}님의 학습")
    
    tab1, tab2 = st.tabs(["문제 풀기", "내 성적"])
    
    with tab1:
        st.subheader("📝 문제 목록")
        
        # 필터링
        col1, col2, col3 = st.columns(3)
        subject_filter = col1.selectbox("과목 필터", ["전체"] + list(set(p['과목'] for p in st.session_state.problems)))
        grade_filter = col2.selectbox("학년 필터", ["전체"] + list(set(p['학년'] for p in st.session_state.problems)))
        type_filter = col3.selectbox("유형 필터", ["전체"] + list(set(p['문제유형'] for p in st.session_state.problems)))
        
        filtered_problems = st.session_state.problems
        
        if subject_filter != "전체":
            filtered_problems = [p for p in filtered_problems if p['과목'] == subject_filter]
        if grade_filter != "전체":
            filtered_problems = [p for p in filtered_problems if p['학년'] == grade_filter]
        if type_filter != "전체":
            filtered_problems = [p for p in filtered_problems if p['문제유형'] == type_filter]
        
        for problem in filtered_problems:
            with st.expander(f"문제 {problem['문제ID']}: {problem['문제내용'][:30]}..."):
                st.write(f"**과목:** {problem['과목']}")
                st.write(f"**학년:** {problem['학년']}")
                st.write(f"**유형:** {problem['문제유형']}")
                st.write(f"**난이도:** {problem['난이도']}")
                st.write(f"**문제 내용:** {problem['문제내용']}")
                
                if problem['문제유형'] == '객관식':
                    for j in range(1, 6):
                        if problem[f'보기{j}']:
                            st.write(f"**보기 {j}:** {problem[f'보기{j}']}")
                
                # 이미 제출했는지 확인
                already_submitted = any(answer[0] == st.session_state.student_id and 
                                       answer[3] == problem['문제ID'] 
                                       for answer in st.session_state.student_answers)
                
                if already_submitted:
                    st.warning("이미 제출한 문제입니다.")
                else:
                    with st.form(f"answer_form_{problem['문제ID']}"):
                        answer = st.text_area("답안 작성")
                        
                        if st.form_submit_button("제출"):
                            if answer:
                                submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                
                                # 채점 로직 (간단히 정확히 일치하는지만 확인)
                                is_correct = answer.strip() == problem['정답'].strip()
                                score = "100" if is_correct else "0"
                                feedback = "정답입니다!" if is_correct else f"오답입니다. 정답은 '{problem['정답']}' 입니다."
                                
                                # 답안 데이터 준비
                                answer_data = [
                                    st.session_state.student_id,
                                    st.session_state.username,
                                    st.session_state.grade,
                                    problem['문제ID'],
                                    answer,
                                    score,
                                    feedback,
                                    submission_time
                                ]
                                
                                st.session_state.student_answers.append(answer_data)
                                
                                if is_correct:
                                    st.success("정답입니다!")
                                else:
                                    st.error(f"오답입니다. 정답은 '{problem['정답']}' 입니다.")
                                    st.info(f"**해설:** {problem['해설']}")
                                
                                st.rerun()
                            else:
                                st.error("답안을 입력해주세요.")
    
    with tab2:
        st.subheader("📊 내 성적")
        
        # 제출한 답안 필터링
        my_answers = [answer for answer in st.session_state.student_answers 
                     if answer[0] == st.session_state.student_id]
        
        if not my_answers:
            st.info("제출한 답안이 없습니다.")
        else:
            # 성적 통계
            correct_answers = [ans for ans in my_answers if ans[5] == "100"]
            total_answers = len(my_answers)
            correct_rate = (len(correct_answers) / total_answers) * 100 if total_answers > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("총 제출 답안", total_answers)
            col2.metric("정답 수", len(correct_answers))
            col3.metric("정답률", f"{correct_rate:.1f}%")
            
            # 개별 답안 목록
            for answer in my_answers:
                with st.expander(f"문제 {answer[3]} ({answer[7]})"):
                    # 문제 찾기
                    problem = None
                    for p in st.session_state.problems:
                        if p['문제ID'] == answer[3]:
                            problem = p
                            break
                    
                    if problem:
                        st.write(f"**문제 내용:** {problem['문제내용']}")
                        st.write(f"**내 답안:** {answer[4]}")
                        st.write(f"**점수:** {answer[5]}")
                        st.write(f"**피드백:** {answer[6]}")
                        st.write(f"**제출 시간:** {answer[7]}")

def main():
    """메인 함수"""
    if not st.session_state.authenticated:
        login_page()
    else:
        # 사이드바
        st.sidebar.title("메뉴")
        
        if st.sidebar.button("로그아웃"):
            st.session_state.authenticated = False
            st.session_state.user_type = None
            st.rerun()
        
        # 페이지 표시
        if st.session_state.user_type == "teacher":
            teacher_dashboard()
        else:
            student_portal()

if __name__ == "__main__":
    main() 