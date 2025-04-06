# 📝 학원 자동 첨삭 시스템 Todo List

## 1. 초기 프로젝트 설정
- [x] 프로젝트 디렉토리 구조 생성
- [x] 필요한 Python 패키지 requirements.txt 작성
  - Streamlit
  - Google Sheets API
  - 기타 필요 라이브러리
- [x] Google Cloud Project 설정 및 credentials.json 획득
- [x] .gitignore 파일 설정 (credentials.json 등 보안 파일 제외)

## 2. Google Sheets 연동
- [x] Google Sheets API 연동 모듈 구현 (sheets/google_sheets.py)
- [x] 시트 구조 설계 및 생성
  - problems 시트: 문제, 난이도, 모범답안, 키워드
  - student_answers 시트: 이름, 학번, 문제ID, 답변, 점수, 피드백
- [x] CRUD 기능 구현
  - 데이터 읽기/쓰기
  - 실시간 업데이트

## 3. 교사용 기능 구현
- [x] 교사 대시보드 페이지 생성 (pages/teacher_dashboard.py)
- [x] 문제 업로드 폼 구현
  - 문제 내용 입력
  - 난이도 선택
  - 모범답안 키워드 등록
- [x] 채점 결과 통계 화면 구현
  - 전체 성적 분포
  - 학생별 성적 현황
  - 문제별 정답률

## 4. 학생용 기능 구현
- [x] 학생 포털 페이지 생성 (pages/student_portal.py)
- [x] 로그인 기능 구현
  - 이름/학번 입력 폼
  - 세션 관리
- [x] 문제 선택 인터페이스
  - 난이도별 문제 목록
  - 문제 상세 보기
- [x] 답안 제출 시스템
  - 답안 입력 폼
  - 제출 확인

## 5. 자동 채점 시스템
- [x] 채점 로직 구현 (logic/grader.py)
  - 키워드 기반 채점 알고리즘
  - 점수 계산 시스템
- [x] 피드백 생성 시스템 (logic/feedback.py)
  - 답안 분석
  - 맞춤형 피드백 생성

## 6. UI/UX
- [ ] Streamlit 테마 설정 (.streamlit/config.toml)
- [ ] 반응형 레이아웃 구현
- [ ] 사용자 친화적 인터페이스 디자인
- [ ] 에러 처리 및 사용자 피드백

## 7. 테스트 및 배포
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 수행
- [ ] Streamlit Community Cloud 배포
- [ ] 사용자 매뉴얼 작성

## 8. 보안 및 데이터 관리
- [ ] 보안 설정 검토
- [ ] 데이터 백업 시스템 구축
- [ ] 에러 로깅 시스템 구현

## 9. 최종 점검
- [ ] 전체 기능 테스트
- [ ] 성능 최적화
- [ ] 사용자 피드백 수집 및 반영
- [ ] 문서화 완료 