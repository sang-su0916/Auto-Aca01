import sys
import os
import subprocess
import time
import webbrowser
from threading import Timer

def ensure_packages():
    """필요한 패키지 설치 확인 및 설치"""
    required_packages = ["streamlit", "pandas"]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} 이미 설치됨")
        except ImportError:
            print(f"! {package} 설치 중...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} 설치 완료")

def create_app_file():
    """임시 앱 파일 생성"""
    app_content = '''
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# CSV 파일 기반 데이터 관리
def load_csv_data():
    try:
        if os.path.exists('sample_questions.csv'):
            problems_df = pd.read_csv('sample_questions.csv', encoding='utf-8')
        else:
            problems_df = pd.DataFrame(columns=[
                '문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설'
            ])
            # 샘플 데이터 생성
            sample_problems = [
                {'문제ID': 'P001', '과목': '영어', '학년': '중3', '문제유형': '객관식', '난이도': '중',
                '문제내용': 'What is the capital of the UK?',
                '보기1': 'London', '보기2': 'Paris', '보기3': 'Berlin', '보기4': 'Rome', '보기5': '',
                '정답': 'London', '키워드': 'capital,UK,London',
                '해설': 'The capital city of the United Kingdom is London.'},
                
                {'문제ID': 'P002', '과목': '영어', '학년': '중3', '문제유형': '주관식', '난이도': '중',
                '문제내용': 'Write a sentence using the word "beautiful".',
                '보기1': '', '보기2': '', '보기3': '', '보기4': '', '보기5': '',
                '정답': 'The flower is beautiful.', '키워드': 'beautiful,sentence',
                '해설': '주어와 동사를 포함한 완전한 문장이어야 합니다.'}
            ]
            problems_df = pd.DataFrame(sample_problems)
            problems_df.to_csv('sample_questions.csv', index=False, encoding='utf-8')
        
        if os.path.exists('student_answers.csv'):
            student_answers_df = pd.read_csv('student_answers.csv', encoding='utf-8')
        else:
            student_answers_df = pd.DataFrame(columns=[
                '학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간'
            ])
            student_answers_df.to_csv('student_answers.csv', index=False, encoding='utf-8')
        
        return problems_df, student_answers_df
    except Exception as e:
        st.error(f"CSV 파일 로드 오류: {str(e)}")
        return None, None

# 자동 채점 기능
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
        
        # 기본 피드백
        return 0, f"오답입니다. 정답은 '{correct_answer}'입니다."
    
    # 서술형 문제 채점
    elif problem_type == '서술형':
        user_answer = user_answer.strip().lower()
        
        # 키워드 기반 채점
        if keywords:
            keyword_list = [k.strip().lower() for k in keywords.split(',')]
            matched_keywords = [k for k in keyword_list if k in user_answer]
            
            score = min(100, int(len(matched_keywords) / len(keyword_list) * 100))
            
            if score >= 80:
                feedback = f"우수한 답변입니다! 포함된 키워드: {', '.join(matched_keywords)}"
            elif score >= 60:
                feedback = f"좋은 답변입니다. 포함된 키워드: {', '.join(matched_keywords)}"
            elif score >= 40:
                feedback = f"보통 수준의 답변입니다. 추가 키워드: {', '.join([k for k in keyword_list if k not in matched_keywords])}"
            else:
                feedback = f"더 자세한 답변이 필요합니다. 주요 키워드: {', '.join(keyword_list)}"
            
            return score, feedback
        
        # 기본 피드백
        return 50, "키워드 정보가 없어 정확한 채점이 어렵습니다. 교사의 확인이 필요합니다."
    
    return 0, "알 수 없는 문제 유형입니다."

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'show_sidebar' not in st.session_state:
    st.session_state.show_sidebar = False

# Set page config
st.set_page_config(
    page_title="학원 자동 첨삭 시스템",
    page_icon="📚",
    initial_sidebar_state="collapsed"
)

# Custom CSS to improve UI
st.markdown('''
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
    .result-card {
        background-color: #f1f8e9;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .feedback-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #2196F3;
    }
</style>
''', unsafe_allow_html=True)

def teacher_dashboard():
    st.title("👨‍🏫 교사 대시보드")
    st.write("문제 관리 및 학생 성적 확인")
    
    tab1, tab2 = st.tabs(["문제 관리", "성적 통계"])
    
    with tab1:
        st.subheader("📝 문제 관리")
        
        # 기존 문제 표시
        problems_df, _ = load_csv_data()
        if problems_df is not None and not problems_df.empty:
            st.subheader("등록된 문제 목록")
            st.dataframe(problems_df)
            st.success(f"총 {len(problems_df)}개의 문제가 등록되어 있습니다.")
        else:
            st.info("현재 등록된 문제가 없습니다.")
        
        # 수동 문제 추가
        st.subheader("📝 문제 직접 추가")
        with st.form("add_problem_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                problem_id = st.text_input("문제ID", value="P" + datetime.now().strftime("%Y%m%d%H%M%S"))
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
                    try:
                        # 기존 문제 로드
                        problems_df, _ = load_csv_data()
                        
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
        _, answers_df = load_csv_data()
        
        if answers_df is not None and not answers_df.empty:
            st.subheader("전체 제출 답안")
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
                
            # 학생별 성적 차트
            st.subheader("학생별 성적")
            student_avg = answers_df.groupby(['학생ID', '이름'])['점수'].mean().reset_index()
            st.bar_chart(student_avg.set_index('이름'))
            
            # 문제별 정답률
            st.subheader("문제별 정답률")
            problem_stats = answers_df.groupby('문제ID')['점수'].agg(['mean', 'count']).reset_index()
            problem_stats.columns = ['문제ID', '평균 점수', '제출 수']
            st.dataframe(problem_stats)
            
        else:
            st.info("아직 제출된 답안이 없습니다.")

def student_portal():
    st.title("👨‍🎓 학생 포털")
    
    # 학생 정보 입력
    if 'student_id' not in st.session_state:
        st.session_state.student_id = ""
        st.session_state.student_name = ""
        st.session_state.student_grade = ""
    
    if not st.session_state.student_id:
        with st.form("student_login"):
            st.subheader("로그인")
            student_id = st.text_input("학생 ID", placeholder="학번을 입력하세요")
            student_name = st.text_input("이름", placeholder="이름을 입력하세요")
            student_grade = st.selectbox("학년", ["", "중1", "중2", "중3", "고1", "고2", "고3"])
            
            submit = st.form_submit_button("로그인")
            
            if submit:
                if student_id and student_name and student_grade:
                    st.session_state.student_id = student_id
                    st.session_state.student_name = student_name
                    st.session_state.student_grade = student_grade
                    st.rerun()
                else:
                    st.error("모든 정보를 입력해주세요.")
    else:
        # 로그인된 상태
        st.write(f"안녕하세요, {st.session_state.student_name}님! ({st.session_state.student_grade})")
        
        if st.button("로그아웃", key="logout"):
            st.session_state.student_id = ""
            st.session_state.student_name = ""
            st.session_state.student_grade = ""
            st.rerun()
        
        # 문제 목록 표시
        st.subheader("📝 문제 목록")
        
        # 필터 옵션
        col1, col2, col3 = st.columns(3)
        with col1:
            subject_filter = st.selectbox("과목", ["전체", "영어", "수학", "국어", "과학", "사회"])
        with col2:
            grade_filter = st.selectbox("학년", ["전체", "중1", "중2", "중3", "고1", "고2", "고3"])
        with col3:
            difficulty_filter = st.selectbox("난이도", ["전체", "상", "중", "하"])
        
        # 문제 데이터 로드
        problems_df, _ = load_csv_data()
        
        if problems_df is not None and not problems_df.empty:
            # 필터링
            filtered_df = problems_df.copy()
            
            if subject_filter != "전체":
                filtered_df = filtered_df[filtered_df['과목'] == subject_filter]
            if grade_filter != "전체":
                filtered_df = filtered_df[filtered_df['학년'] == grade_filter]
            if difficulty_filter != "전체":
                filtered_df = filtered_df[filtered_df['난이도'] == difficulty_filter]
            
            if not filtered_df.empty:
                for _, problem in filtered_df.iterrows():
                    with st.expander(f"{problem['문제ID']} - {problem['문제내용'][:30]}... ({problem['과목']}, {problem['학년']}, {problem['난이도']})"):
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
                            # 주관식/서술형 문제
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
                            st.markdown(f"""
                            <div class="result-card">
                                <h4>채점 결과</h4>
                                <p>점수: {score}/100</p>
                                <div class="feedback-box">
                                    <p><strong>피드백:</strong> {feedback}</p>
                                </div>
                                <p><strong>해설:</strong> {problem['해설']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # CSV 파일에 저장
                            try:
                                # 기존 답안 데이터 로드
                                _, answers_df = load_csv_data()
                                
                                # 새 답안 추가
                                new_answer = pd.DataFrame([{
                                    '학생ID': st.session_state.student_id,
                                    '이름': st.session_state.student_name,
                                    '학년': st.session_state.student_grade,
                                    '문제ID': problem['문제ID'],
                                    '제출답안': user_answer,
                                    '점수': score,
                                    '피드백': feedback,
                                    '제출시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }])
                                
                                # 답안 추가 및 저장
                                if answers_df is None:
                                    answers_df = new_answer
                                else:
                                    answers_df = pd.concat([answers_df, new_answer], ignore_index=True)
                                
                                answers_df.to_csv('student_answers.csv', index=False, encoding='utf-8')
                                st.success("답안이 성공적으로 제출되었습니다!")
                            except Exception as e:
                                st.error(f"답안 저장 중 오류가 발생했습니다: {str(e)}")
            else:
                st.info("조건에 맞는 문제가 없습니다.")
        else:
            st.info("등록된 문제가 없습니다.")

def login():
    st.title("🏫 학원 자동 첨삭 시스템")
    
    if st.session_state.authenticated:
        # 이미 인증됨
        # 사이드바 표시
        st.session_state.show_sidebar = True
        st.write("관리자로 로그인되었습니다.")
        
        # 교사 대시보드 표시
        teacher_dashboard()
        
        # 로그아웃 버튼
        if st.button("로그아웃"):
            st.session_state.authenticated = False
            st.session_state.show_sidebar = False
            st.rerun()
    else:
        # 인증 폼
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👨‍🏫 교사 로그인")
            with st.form("teacher_login"):
                teacher_id = st.text_input("교사 ID", placeholder="관리자 ID를 입력하세요")
                password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
                submit = st.form_submit_button("로그인")
                
                if submit:
                    # 간단한 인증 (실제로는 더 안전한 방법 사용)
                    if teacher_id == "admin" and password == "1234":
                        st.session_state.authenticated = True
                        st.session_state.show_sidebar = True
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 잘못되었습니다.")
        
        with col2:
            st.subheader("👨‍🎓 학생 포털")
            if st.button("학생 포털로 이동"):
                st.session_state.page = "student"
                st.rerun()

def main():
    # 페이지 상태 관리
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    
    # 페이지 라우팅
    if st.session_state.page == "login":
        login()
    elif st.session_state.page == "student":
        student_portal()
    
    # 홈으로 돌아가기 버튼
    if st.session_state.page != "login":
        if st.button("홈으로 돌아가기"):
            st.session_state.page = "login"
            st.rerun()

main()
"""
    
    with open("temp_app.py", "w", encoding="utf-8") as f:
        f.write(app_content)
    
    print(f"✓ 임시 앱 파일 생성 완료")

def open_browser():
    """웹 브라우저 열기"""
    time.sleep(3)  # 3초 대기
    webbrowser.open("http://localhost:8501")

def main():
    """메인 함수"""
    print("========= 학원 자동 첨삭 시스템 통합 실행기 =========")
    print("필요한 준비를 진행합니다...")
    
    # 패키지 설치 확인
    ensure_packages()
    
    # 임시 앱 파일 생성
    create_app_file()
    
    # 브라우저 자동 실행
    print("앱 시작 중... 잠시 후 브라우저가 자동으로 열립니다.")
    Timer(2, open_browser).start()
    
    # Streamlit 실행
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "temp_app.py"])
    except KeyboardInterrupt:
        print("\n사용자에 의해 종료되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 임시 파일 정리
        try:
            os.remove("temp_app.py")
            print("임시 파일 정리 완료")
        except:
            pass

if __name__ == "__main__":
    main() 