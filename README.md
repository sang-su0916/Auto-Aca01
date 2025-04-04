# 📚 학원 자동 첨삭 시스템

영어 문제 자동 채점 및 피드백 시스템입니다.

## 🚀 실행 방법

### 원클릭 실행
1. `학원 자동 첨삭 시스템.bat` 파일을 더블클릭하세요.
2. 시스템이 자동으로 실행됩니다.

### 수동 실행 (개발자용)
1. Python 환경 설정:
```bash
# 가상환경 생성 (최초 1회)
python -m venv venv

# 가상환경 활성화
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 필요 패키지 설치
pip install -r requirements.txt
```

2. 시스템 실행:
```bash
streamlit run app.py
```

3. 브라우저에서 접속:
```
http://localhost:8501
```

## 🌐 Streamlit Cloud 배포

이 프로젝트는 Streamlit Cloud를 통해 배포할 수 있습니다:

1. [Streamlit Cloud](https://streamlit.io/cloud)에 가입하고 GitHub 계정을 연결합니다.
2. "New app" 버튼을 클릭합니다.
3. GitHub 저장소와 브랜치를 선택합니다.
4. 메인 파일로 `app.py`를 지정합니다.
5. 고급 설정에서 다음 비밀 환경변수를 설정합니다:
   - `GOOGLE_SHEETS_SPREADSHEET_ID` : 연결할 Google Sheets ID

6. "Deploy" 버튼을 클릭하여 배포합니다.

### 중요 참고사항
- Streamlit Cloud에 배포하려면 `credentials.json` 파일의 내용을 비밀 환경변수로 설정해야 합니다.
- `credentials.json` 파일의 내용을 `GOOGLE_APPLICATION_CREDENTIALS_JSON`라는 이름의 비밀 환경변수에 복사하세요.

## 📝 사용 가이드

### 교사 계정
- 아이디: teacher
- 비밀번호: demo1234
- 기능: 문제 관리, 학생 답안 확인, 채점

### 학생 계정
- 아이디: student
- 비밀번호: demo5678
- 기능: 문제 풀기, 성적 확인

## 🛠️ 기술 스택
- Python
- Streamlit
- Google Sheets API

## 📋 기능

- **교사 기능**:
  - 문제 관리 (추가, 보기)
  - 학생 답안 확인
  - 성적 통계 확인

- **학생 기능**:
  - 문제 선택 및 풀기
  - 자동 채점 확인
  - 성적 통계 확인

## 🔑 데모 계정

아래 계정으로 테스트할 수 있습니다:

### 교사 계정
- 아이디: teacher
- 비밀번호: demo1234

### 학생 계정
- 아이디: student
- 비밀번호: demo5678

## 📝 문제 해결

### 실행이 안될 때 해결 방법

1. **원클릭 실행**: `학원 자동 첨삭 시스템.bat` 파일을 더블클릭

2. **pyvenv.cfg 오류**:
   다음 명령어로 실행하여 오류를 우회할 수 있습니다:
   ```
   py no_dependency_app.py
   ```
   또는 배치 파일을 실행하세요:
   ```
   start.bat
   ```

3. **Python 설치 확인**:
   - 명령 프롬프트에서 `py -V` 또는 `python -V` 실행
   - 오류가 발생하면 Python 설치 필요 (https://www.python.org/downloads/)
   - 설치 시 "Add Python to PATH" 옵션 선택

### 외부 의존성 문제

`no_dependency_app.py`는 표준 라이브러리만 사용하여 외부 패키지나 가상환경 없이 작동합니다.
데이터는 `data` 폴더의 JSON 파일에 저장됩니다. 