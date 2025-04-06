import streamlit as st
import pandas as pd
import os
import base64

def get_table_download_link(filename):
    """Generate a link to download the sample CSV file"""
    with open(filename) as f:
        csv = f.read()
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">샘플 CSV 파일 다운로드</a>'
    return href

def validate_csv(df):
    """Validate the uploaded CSV file format"""
    required_columns = ['문제 ID', '과목', '학년', '문제 유형', '난이도', '문제', '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"다음 필수 열이 누락되었습니다: {', '.join(missing_columns)}"
    
    # 학년 검증
    valid_grades = ['중1', '중2', '중3', '고1', '고2', '고3']
    invalid_grades = df[~df['학년'].isin(valid_grades)]['학년'].unique()
    if len(invalid_grades) > 0:
        return False, f"잘못된 학년이 포함되어 있습니다: {', '.join(invalid_grades)}"
    
    # 문제 유형 검증
    valid_types = ['객관식', '주관식', '서술형']
    invalid_types = df[~df['문제 유형'].isin(valid_types)]['문제 유형'].unique()
    if len(invalid_types) > 0:
        return False, f"잘못된 문제 유형이 포함되어 있습니다: {', '.join(invalid_types)}"
    
    # 난이도 검증
    valid_levels = ['상', '중', '하']
    invalid_levels = df[~df['난이도'].isin(valid_levels)]['난이도'].unique()
    if len(invalid_levels) > 0:
        return False, f"잘못된 난이도가 포함되어 있습니다: {', '.join(invalid_levels)}"
    
    return True, "검증 완료"

def app():
    st.title("문제 업로드")
    
    st.markdown("### 문제 업로드 가이드")
    st.write("""
    1. 문제는 CSV 파일 형식으로 업로드해주세요.
    2. 아래 샘플 파일을 다운로드하여 형식을 확인할 수 있습니다.
    3. 문제 유형은 객관식, 주관식, 서술형 중 하나를 선택해주세요.
    4. 학년은 중1, 중2, 중3, 고1, 고2, 고3 중 하나를 선택해주세요.
    5. 난이도는 상, 중, 하 중 하나를 선택해주세요.
    """)
    
    st.markdown(get_table_download_link('sample_problems.csv'), unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            is_valid, message = validate_csv(df)
            
            if is_valid:
                st.success("파일이 성공적으로 검증되었습니다.")
                st.write("업로드된 문제 목록:")
                st.dataframe(df)
                
                if st.button("문제 등록"):
                    # TODO: Google Sheets에 데이터 저장 로직 구현
                    st.success("문제가 성공적으로 등록되었습니다!")
            else:
                st.error(message)
                
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    app() 