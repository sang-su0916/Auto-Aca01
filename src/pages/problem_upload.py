import streamlit as st
import sys
import os
import pandas as pd
import datetime
import uuid
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.sheets.google_sheets import GoogleSheetsManager

def initialize_session_state():
    """세션 상태 초기화"""
    if 'is_teacher' not in st.session_state:
        st.session_state.is_teacher = False
    if 'teacher_password' not in st.session_state:
        # 실제 애플리케이션에서는 더 안전한 인증 방식 사용 권장
        st.session_state.teacher_password = "teacher123"
    if 'sheets_manager' not in st.session_state:
        # 기본 credentials.json 위치 (나중에 환경 변수로 설정 가능)
        credentials_path = 'credentials.json'
        spreadsheet_id = os.getenv('SPREADSHEET_ID', None)
        
        # Google Sheets 연결 초기화
        st.session_state.sheets_manager = GoogleSheetsManager(
            credentials_path=credentials_path,
            spreadsheet_id=spreadsheet_id
        )

def login_form():
    """교사 로그인 폼"""
    st.header("🔐 교사 로그인")
    
    with st.form("teacher_login_form"):
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")
        
        if submitted:
            if password == st.session_state.teacher_password:
                st.session_state.is_teacher = True
                st.success("로그인 성공!")
                st.experimental_rerun()
            else:
                st.error("비밀번호가 일치하지 않습니다.")

def problem_upload_form():
    """문제 업로드 폼"""
    st.header("📝 문제 업로드")
    
    with st.form("problem_upload_form"):
        # 문제 기본 정보
        problem_id = st.text_input("문제 ID", value=f"P{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        problem_text = st.text_area("문제 내용", placeholder="학생들에게 제시할 문제를 입력하세요")
        
        # 난이도 선택 (상/중/하)
        difficulty = st.selectbox("난이도", ["상", "중", "하"])
        
        # 모범 답안 및 키워드
        model_answer = st.text_area("모범 답안", placeholder="정답으로 인정할 수 있는 모범 답안을 입력하세요")
        keywords = st.text_input("채점 키워드", placeholder="콤마(,)로 구분하여 입력 (예: 태양계,행성,공전)")
        
        submitted = st.form_submit_button("문제 등록")
        
        if submitted:
            if problem_text and model_answer and keywords:
                # Google Sheets에 문제 추가
                success = add_problem(problem_id, problem_text, difficulty, model_answer, keywords)
                if success:
                    st.success("문제가 성공적으로 등록되었습니다.")
                    # 입력 폼 초기화 (새 문제 ID 생성)
                    st.experimental_rerun()
            else:
                st.error("문제 내용, 모범 답안, 채점 키워드는 필수 입력 항목입니다.")

def add_problem(problem_id, problem_text, difficulty, model_answer, keywords):
    """문제를 Google Sheets에 추가"""
    try:
        sheets_manager = st.session_state.sheets_manager
        
        # 키워드를 리스트로 변환
        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        
        # 문제 추가
        success = sheets_manager.add_problem(
            problem_id=problem_id, 
            problem_text=problem_text, 
            difficulty=difficulty, 
            model_answer=model_answer, 
            keywords=keyword_list
        )
        
        return success
    except Exception as e:
        st.error(f"문제 등록 오류: {e}")
        return False

def csv_uploader():
    """CSV 파일을 통한 대량 문제 업로드"""
    st.header("📊 CSV 파일로 문제 업로드")
    
    st.write("여러 문제를 한 번에 업로드하려면 CSV 파일을 사용하세요.")
    
    # CSV 템플릿 다운로드 링크
    st.markdown("""
    ### CSV 파일 형식
    다음 열을 포함해야 합니다:
    - `문제ID`: 고유 식별자
    - `문제`: 문제 내용
    - `난이도`: 상, 중, 하 중 하나
    - `모범답안`: 예시 정답
    - `키워드`: 콤마(,)로 구분된 키워드
    """)
    
    # 예시 데이터로 CSV 템플릿 생성
    example_data = pd.DataFrame({
        '문제ID': ['P00001', 'P00002'],
        '문제': ['태양계의 구성에 대해 설명하시오.', '지구의 자전과 공전에 대해 설명하시오.'],
        '난이도': ['중', '하'],
        '모범답안': ['태양계는 태양을 중심으로 8개의 행성이 공전한다...', '지구는 자전축을 중심으로 24시간에 한 바퀴씩 자전하고...'],
        '키워드': ['태양,행성,공전,태양계', '지구,자전,공전,자전축,계절']
    })
    
    # CSV 템플릿 다운로드 버튼
    csv = example_data.to_csv(index=False)
    st.download_button(
        label="CSV 템플릿 다운로드",
        data=csv,
        file_name="problems_template.csv",
        mime="text/csv"
    )
    
    # CSV 파일 업로드
    uploaded_file = st.file_uploader("CSV 파일 선택", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # 필수 열 확인
            required_columns = ['문제ID', '문제', '난이도', '모범답안', '키워드']
            if not all(col in df.columns for col in required_columns):
                st.error(f"CSV 파일에 필수 열이 없습니다. 필요한 열: {', '.join(required_columns)}")
                return
            
            # 미리보기 표시
            st.subheader("데이터 미리보기")
            st.dataframe(df.head())
            
            # 업로드 버튼
            if st.button("문제 일괄 등록"):
                with st.spinner("문제를 등록 중입니다..."):
                    success_count = 0
                    error_count = 0
                    
                    sheets_manager = st.session_state.sheets_manager
                    
                    for _, row in df.iterrows():
                        try:
                            # 문제 추가
                            success = sheets_manager.add_problem(
                                problem_id=row['문제ID'],
                                problem_text=row['문제'],
                                difficulty=row['난이도'],
                                model_answer=row['모범답안'],
                                keywords=row['키워드']
                            )
                            
                            if success:
                                success_count += 1
                            else:
                                error_count += 1
                                
                        except Exception:
                            error_count += 1
                    
                    # 결과 표시
                    st.success(f"{success_count}개 문제가 성공적으로 등록되었습니다.")
                    if error_count > 0:
                        st.warning(f"{error_count}개 문제 등록 중 오류가 발생했습니다.")
                
        except Exception as e:
            st.error(f"파일 처리 오류: {e}")

def display_problem_list():
    """등록된 문제 목록 표시"""
    st.header("📋 등록된 문제 목록")
    
    try:
        # 문제 로드
        sheets_manager = st.session_state.sheets_manager
        problems = sheets_manager.get_problems()
        
        if not problems:
            st.info("등록된 문제가 없습니다.")
            return
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(problems)
        
        # 키워드 열 처리 (리스트를 문자열로 변환)
        if '키워드' in df.columns:
            df['키워드'] = df['키워드'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        
        # 난이도별 필터링
        difficulties = ["전체"] + sorted(df['난이도'].unique().tolist())
        selected_difficulty = st.selectbox("난이도 필터", difficulties)
        
        if selected_difficulty != "전체":
            filtered_df = df[df['난이도'] == selected_difficulty]
        else:
            filtered_df = df
            
        # 필터링된 데이터 표시
        st.dataframe(filtered_df)
        
        # 통계 정보
        st.subheader("📊 문제 통계")
        
        col1, col2 = st.columns(2)
        with col1:
            difficulty_counts = df['난이도'].value_counts()
            st.bar_chart(difficulty_counts)
        
        with col2:
            st.metric("총 문제 수", len(df))
            st.write("난이도별 문제 수:")
            for diff, count in difficulty_counts.items():
                st.write(f"- {diff}: {count}개")
        
    except Exception as e:
        st.error(f"문제 목록 로드 오류: {e}")

def display_student_answers():
    """학생 답안 목록 표시"""
    st.header("✏️ 학생 답안 제출 현황")
    
    try:
        sheets_manager = st.session_state.sheets_manager
        answers = sheets_manager.get_student_answers()
        
        if not answers:
            st.info("제출된 답안이 없습니다.")
            return
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(answers)
        
        # 학생별 필터링
        students = ["전체"] + sorted(df['이름'].unique().tolist())
        selected_student = st.selectbox("학생 필터", students)
        
        if selected_student != "전체":
            filtered_df = df[df['이름'] == selected_student]
        else:
            filtered_df = df
        
        # 필터링된 데이터 표시
        st.dataframe(filtered_df)
        
        # 통계 정보
        if len(filtered_df) > 0:
            st.subheader("📈 성적 통계")
            
            # 점수 열이 있고 숫자로 변환 가능한 경우에만 통계 계산
            if '점수' in filtered_df.columns:
                try:
                    # 점수를 숫자로 변환 (빈 문자열이나 누락된 값은 NaN으로)
                    filtered_df['점수'] = pd.to_numeric(filtered_df['점수'], errors='coerce')
                    
                    # 통계 계산
                    avg_score = filtered_df['점수'].mean()
                    max_score = filtered_df['점수'].max()
                    min_score = filtered_df['점수'].min()
                    
                    # 통계 표시
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("평균 점수", f"{avg_score:.1f}")
                    with col2:
                        st.metric("최고 점수", f"{max_score:.1f}")
                    with col3:
                        st.metric("최저 점수", f"{min_score:.1f}")
                    
                    # 히스토그램 표시
                    st.subheader("점수 분포")
                    hist_values = filtered_df['점수'].dropna()
                    if len(hist_values) > 0:
                        st.bar_chart(hist_values.value_counts().sort_index())
                
                except Exception as e:
                    st.warning(f"점수 통계 계산 오류: {e}")
        
    except Exception as e:
        st.error(f"학생 답안 로드 오류: {e}")

def main():
    """메인 함수"""
    st.title("🏫 학원 자동 첨삭 시스템 - 교사 포털")
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 사이드바에 교사 상태 표시
    with st.sidebar:
        if st.session_state.is_teacher:
            st.success("교사 로그인 성공")
            if st.button("로그아웃"):
                st.session_state.is_teacher = False
                st.experimental_rerun()
        else:
            st.info("교사 로그인이 필요합니다.")
    
    # 로그인 상태에 따른 화면 표시
    if not st.session_state.is_teacher:
        login_form()
    else:
        # 탭 구성
        tab1, tab2, tab3, tab4 = st.tabs([
            "문제 업로드", "CSV 일괄 업로드", "문제 목록", "학생 답안 현황"
        ])
        
        with tab1:
            problem_upload_form()
        
        with tab2:
            csv_uploader()
        
        with tab3:
            display_problem_list()
        
        with tab4:
            display_student_answers()

if __name__ == "__main__":
    main() 