## 📘 PRD 문서: 학원 자동 첨삭 시스템 (MVP 버전)

---

### 1. 프로젝트 개요

교사는 난이도별 문제를 업로드하고, 학생은 개인 수준에 맞는 문제를 선택하여 답안을 작성합니다.  
제출된 답안은 자동으로 채점 및 첨삭되며, 모든 결과는 Google Sheets로 저장됩니다.  
**비개발자도 운영할 수 있는 Streamlit 기반 시스템**으로, 학원 수업의 효율성과 피드백의 품질을 동시에 높입니다.

---

### 2. 핵심 기능 (Core Functionalities)

#### 🧑‍🏫 교사용 기능
- 문제 업로드 (난이도 포함)
- 모범답안 키워드 등록
- 채점 결과 통계 확인 (Google Sheets 기반)

#### 🧑‍🎓 학생용 기능
- 이름/학번으로 로그인
- 난이도에 맞는 문제 선택
- 답안 제출 → 자동 채점 및 첨삭 피드백
- 본인 결과 확인

#### 🔄 공통 기능
- Google Sheets 자동 연동 (모든 데이터 기록/복원)
- 역할 기반 화면 분리 (학생 vs 교사)
- 문제/답안/결과 실시간 시트 반영

---

### 3. 기술 스펙 (Tech Stack & Doc)

| 항목 | 내용 |
|------|------|
| 프론트/UI | Streamlit |
| 채점/첨삭 | Python 키워드 기반 자동 채점 |
| 백업/저장소 | Google Sheets API |
| 개발환경 | Cursor IDE, GitHub |
| 배포 방식 | Streamlit Community Cloud (무설정 무료 배포) |

---

### 4. 파일 구조 예시 (File Structure)

```
auto_academy/
├── app.py                      # Streamlit 메인 진입점
├── pages/
│   ├── student_portal.py       # 학생용 페이지
│   └── teacher_dashboard.py    # 교사용 페이지 (추후 추가 가능)
├── logic/
│   ├── grader.py               # 채점 로직
│   └── feedback.py             # (선택) 추가 첨삭 분석
├── sheets/
│   └── google_sheets.py        # Sheets 연동 모듈
├── data/
│   ├── problems.csv            # 문제 데이터 (초기 셋업용)
│   └── model_answers.csv       # 정답 키워드
├── credentials.json            # 구글 API 인증키
└── .streamlit/
    └── config.toml             # 스트림릿 설정 파일
```

---

### 5. 추가 요구사항 (Additional Requirements)

- Google Sheets 시트 구성  
  - `problems`: 문제, 난이도, 모범답안, 키워드  
  - `student_answers`: 이름, 학번, 문제ID, 답변, 점수, 피드백  
- Streamlit에서 간단한 UI 폼 제공 (버튼, 입력창 등)
- 답안 제출 후 실시간 결과 확인 (성적 + 피드백)
- 관리자(교사)는 Google Sheets에서 직접 성적 열람/분석 가능

---

### ✅ 예상 사용자 흐름

1. 교사: 문제 등록 → 키워드 입력 → 시트에 자동 저장  
2. 학생: 로그인 → 난이도 선택 → 문제 확인 → 답안 제출  
3. 자동 채점 + 피드백 생성  
4. 결과는 Google Sheets에 자동 저장  
5. 학생은 즉시 결과 확인, 교사는 시트 분석 가능
