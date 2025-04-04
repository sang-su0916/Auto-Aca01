import streamlit as st
import pandas as pd
import json
import os

# 앱 설정
st.set_page_config(
    page_title="CSV 파일 업로드 도우미",
    page_icon="📚",
    layout="wide"
)

st.title("📚 CSV 문제 데이터 업로드 도우미")

st.markdown("""
이 도구는 CSV 형식의 문제 데이터를 시스템에서 사용할 수 있는 형식으로 변환해줍니다.
CSV 파일을 업로드하면, 앱의 세션 상태에 문제 데이터를 저장합니다.
""")

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

# CSV 파일 업로드
st.subheader("CSV 파일 업로드")
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
        else:
            # 옵션 컬럼 확인 및 추가
            option_columns = ["보기1", "보기2", "보기3", "보기4", "보기5"]
            for col in option_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # 데이터 변환
            problems = []
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
                problems.append(problem)
            
            # 세션 상태에 저장
            if 'problems' not in st.session_state:
                st.session_state.problems = []
            
            # 기존 문제 목록과 병합할지 결정
            if st.session_state.problems:
                merge_option = st.radio(
                    "기존 문제와 병합하시겠습니까?",
                    ["새 문제로 대체", "기존 문제에 추가"]
                )
                
                if merge_option == "새 문제로 대체":
                    st.session_state.problems = problems
                    st.success(f"{len(problems)}개의 문제가 업로드되었습니다. 기존 문제는 제거되었습니다.")
                else:
                    # 중복 문제ID 확인
                    existing_ids = {p['문제ID'] for p in st.session_state.problems}
                    new_problems = []
                    duplicate_ids = []
                    
                    for problem in problems:
                        if problem['문제ID'] in existing_ids:
                            duplicate_ids.append(problem['문제ID'])
                        else:
                            new_problems.append(problem)
                            existing_ids.add(problem['문제ID'])
                    
                    if duplicate_ids:
                        handle_duplicates = st.radio(
                            "중복된 문제ID가 있습니다. 어떻게 처리하시겠습니까?",
                            ["건너뛰기", "덮어쓰기"]
                        )
                        
                        if handle_duplicates == "덮어쓰기":
                            # 중복 제거
                            st.session_state.problems = [p for p in st.session_state.problems if p['문제ID'] not in [np['문제ID'] for np in problems]]
                            st.session_state.problems.extend(problems)
                            st.success(f"{len(problems)}개의 문제가 업로드되었습니다. {len(duplicate_ids)}개의 중복 문제가 덮어쓰기되었습니다.")
                        else:
                            st.session_state.problems.extend(new_problems)
                            st.success(f"{len(new_problems)}개의 새 문제가 추가되었습니다. {len(duplicate_ids)}개의 중복 문제는 건너뛰었습니다.")
                    else:
                        st.session_state.problems.extend(problems)
                        st.success(f"{len(problems)}개의 문제가 기존 목록에 추가되었습니다.")
            else:
                st.session_state.problems = problems
                st.success(f"{len(problems)}개의 문제가 업로드되었습니다.")
            
            # 미리보기
            st.subheader("업로드된 문제 미리보기")
            st.dataframe(df)
            
            # JSON 저장 옵션
            if st.button("JSON 파일로 저장"):
                json_data = json.dumps(problems, ensure_ascii=False, indent=4)
                st.download_button(
                    label="JSON 다운로드",
                    data=json_data,
                    file_name="problems.json",
                    mime="application/json"
                )
    
    except Exception as e:
        st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")

# 사용 방법 안내
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

with st.expander("이 도구 사용법"):
    st.markdown("""
    ### 사용 방법
    
    1. 상단의 '샘플 CSV 파일 다운로드' 버튼을 클릭하여 샘플 파일을 다운로드합니다.
    2. 샘플 파일을 참고하여 CSV 파일을 준비합니다.
    3. 'CSV 파일을 업로드하세요' 버튼을 클릭하여 파일을 업로드합니다.
    4. 파일이 성공적으로 처리되면 미리보기가 표시됩니다.
    5. 필요한 경우 'JSON 파일로 저장' 버튼을 클릭하여 JSON 형식으로 저장할 수 있습니다.
    
    업로드된 문제는 앱의 세션 상태(`st.session_state.problems`)에 저장되며, 브라우저를 닫거나 앱을 재시작하면 초기화됩니다.
    영구적으로 저장하려면 JSON 파일로 다운로드하여 보관하세요.
    """)

# 푸터
st.markdown("---")
st.markdown("© 2025 학원 자동 첨삭 시스템") 