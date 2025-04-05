import streamlit as st
import pandas as pd
from datetime import datetime
import random
import os
from pathlib import Path

# 구글 시트 연동 모듈 불러오기
try:
    from sheets.google_sheets import GoogleSheetsAPI
    sheets_api = GoogleSheetsAPI()
    USE_GOOGLE_SHEETS = True
except Exception as e:
    print(f"구글 시트 연동 오류: {e}")
    USE_GOOGLE_SHEETS = False

# 페이지 설정
st.set_page_config(
    page_title="학원 자동 첨삭 시스템",
    page_icon="📚",
    layout="wide"
)

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'scores' not in st.session_state:
    st.session_state.scores = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# 기본 사용자 데이터 (실제로는 데이터베이스에서 가져와야 함)
users = {
    "admin": {"password": "1234", "name": "관리자", "role": "teacher"},
    "student1": {"password": "1234", "name": "홍길동", "role": "student", "grade": "중3"},
    "student2": {"password": "1234", "name": "김철수", "role": "student", "grade": "중2"},
    "student3": {"password": "1234", "name": "박영희", "role": "student", "grade": "중1"}
}

# 문제 불러오기 함수
def load_questions():
    if USE_GOOGLE_SHEETS:
        try:
            # 구글 시트에서 문제 데이터 가져오기
            problems_data = sheets_api.read_range('problems!A2:N')
            if not problems_data:
                return generate_default_questions()
            
            questions = []
            for row in problems_data:
                if len(row) >= 12:  # 최소 필수 필드 확인
                    question = {
                        "id": row[0],
                        "subject": row[1],
                        "grade": row[2],
                        "type": row[3],
                        "difficulty": row[4],
                        "content": row[5],
                        "options": [row[6], row[7], row[8], row[9]],
                        "answer": row[11],
                        "keywords": row[12] if len(row) > 12 else "",
                        "explanation": row[13] if len(row) > 13 else ""
                    }
                    questions.append(question)
            return questions
        except Exception as e:
            print(f"구글 시트에서 문제 불러오기 오류: {e}")
            return generate_default_questions()
    else:
        return generate_default_questions()

# 기본 문제 생성 함수
def generate_default_questions():
    # 중2 시간 관련 영어 문제
    time_questions = []
    
    for i in range(20):
        hour = random.randint(1, 12)
        minute = random.choice([0, 15, 30, 45])
        
        if minute == 0:
            answer = f"{hour} o'clock"
        elif minute == 15:
            answer = f"quarter past {hour}"
        elif minute == 30:
            answer = f"half past {hour}"
        elif minute == 45:
            answer = f"quarter to {(hour % 12) + 1}"
        
        options = [answer]
        while len(options) < 4:
            h = random.randint(1, 12)
            m = random.choice([0, 15, 30, 45])
            
            if m == 0:
                opt = f"{h} o'clock"
            elif m == 15:
                opt = f"quarter past {h}"
            elif m == 30:
                opt = f"half past {h}"
            elif m == 45:
                opt = f"quarter to {(h % 12) + 1}"
                
            if opt not in options:
                options.append(opt)
                
        random.shuffle(options)
        
        time_questions.append({
            "id": f"G2-T{i+1}",
            "subject": "영어",
            "grade": "중2",
            "type": "multiple_choice",
            "difficulty": "중",
            "content": f"What time is it? (시계 이미지: {hour}:{minute:02d})",
            "options": options,
            "answer": answer,
            "keywords": "time,clock,hour",
            "explanation": f"The correct time is {answer}."
        })
    
    return time_questions

# 중2 영어 문제 생성 함수
def generate_grade2_questions():
    questions = []
    
    # 중2 시간 관련 영어 문제
    time_questions = [
        {
            "id": f"G2-T{i+1}",
            "content": f"What time is it? (시계 이미지: {random.randint(1, 12)}:{random.randint(0, 59):02d})",
            "options": ["quarter past two", "half past three", "quarter to five", "ten to six"],
            "answer": random.randint(0, 3),
            "type": "multiple_choice",
            "difficulty": "중",
            "grade": "중2",
            "category": "time"
        } for i in range(20)
    ]
    
    # 정답 및 선택지 업데이트
    for q in time_questions:
        time_str = q["content"].split("시계 이미지: ")[1].strip(")")
        hour, minute = map(int, time_str.split(":"))
        
        if minute == 0:
            answer = f"{hour} o'clock"
        elif minute == 15:
            answer = f"quarter past {hour}"
        elif minute == 30:
            answer = f"half past {hour}"
        elif minute == 45:
            answer = f"quarter to {(hour % 12) + 1}"
        elif minute < 30:
            answer = f"{minute} minutes past {hour}"
        else:
            answer = f"{60 - minute} minutes to {(hour % 12) + 1}"
            
        options = [answer]
        while len(options) < 4:
            h = random.randint(1, 12)
            m = random.choice([0, 15, 30, 45, random.randint(1, 59)])
            
            if m == 0:
                opt = f"{h} o'clock"
            elif m == 15:
                opt = f"quarter past {h}"
            elif m == 30:
                opt = f"half past {h}"
            elif m == 45:
                opt = f"quarter to {(h % 12) + 1}"
            elif m < 30:
                opt = f"{m} minutes past {h}"
            else:
                opt = f"{60 - m} minutes to {(h % 12) + 1}"
                
            if opt not in options:
                options.append(opt)
                
        random.shuffle(options)
        q["options"] = options
        q["answer"] = options.index(answer)
        q["content"] = f"What time is it? (시계 이미지: {hour}:{minute:02d})"
        
    questions.extend(time_questions)
    return questions

# 채점 함수
def grade_answer(question, user_answer):
    if question["type"] == "multiple_choice":
        correct = question["options"][question["answer"]]
        user_choice = question["options"][user_answer] if isinstance(user_answer, int) else user_answer
        is_correct = user_choice == correct
        score = 5 if is_correct else 0
        feedback = "정답입니다! 🎉" if is_correct else f"오답입니다. 정답은 '{correct}'입니다."
        
        # 구글 시트에 답안 저장
        if USE_GOOGLE_SHEETS and st.session_state.authenticated:
            try:
                sheets_api.append_row('student_answers', [
                    st.session_state.user_data["username"],
                    st.session_state.user_data["name"],
                    st.session_state.user_data.get("grade", ""),
                    question["id"],
                    user_choice,
                    score,
                    feedback,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
            except Exception as e:
                print(f"구글 시트에 답안 저장 오류: {e}")
        
        return {
            "score": score,
            "feedback": feedback,
            "is_correct": is_correct,
            "correct_answer": correct
        }
    else:  # open_ended
        keywords = question["keywords"]
        score = 0
        matched_keywords = []
        
        for keyword, value in keywords.items():
            if keyword.lower() in user_answer.lower():
                score += value
                matched_keywords.append(keyword)
                
        score = min(score, 5)  # 최대 5점
        
        if score == 5:
            feedback = "완벽한 답변입니다! 🎉"
        elif score >= 3:
            feedback = f"좋은 답변입니다! 다음 키워드를 포함했습니다: {', '.join(matched_keywords)}"
        elif score > 0:
            feedback = f"부분적으로 맞았습니다. 포함된 키워드: {', '.join(matched_keywords)}"
        else:
            feedback = "핵심 키워드가 없습니다. 다시 시도해보세요."
        
        # 구글 시트에 답안 저장
        if USE_GOOGLE_SHEETS and st.session_state.authenticated:
            try:
                sheets_api.append_row('student_answers', [
                    st.session_state.user_data["username"],
                    st.session_state.user_data["name"],
                    st.session_state.user_data.get("grade", ""),
                    question["id"],
                    user_answer,
                    score,
                    feedback,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
            except Exception as e:
                print(f"구글 시트에 답안 저장 오류: {e}")
            
        return {
            "score": score,
            "feedback": feedback,
            "is_correct": score >= 3,
            "matched_keywords": matched_keywords
        }

# 로그아웃 함수
def logout():
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.session_state.current_question_index = 0
    st.session_state.answers = {}
    st.session_state.scores = {}
    st.session_state.submitted = False

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #0D47A1;
        margin-bottom: 0.5rem;
    }
    .question-container {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .info-text {
        color: #555;
        font-size: 1rem;
    }
    .correct-answer {
        color: #4CAF50;
        font-weight: bold;
    }
    .wrong-answer {
        color: #F44336;
    }
    .nav-button {
        margin-right: 0.5rem;
    }
    .score-text {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .feedback-text {
        margin-top: 0.5rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# 메인 앱
def main():
    # 로그인 상태가 아니면 로그인 화면 표시
    if not st.session_state.authenticated:
        login()
    else:
        # 사용자 정보 표시
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown(f"<h1 class='main-header'>학생 포털 - {st.session_state.user_data['name']} ({st.session_state.user_data.get('grade', '')})</h1>", unsafe_allow_html=True)

        # 로그아웃 버튼
        if st.sidebar.button("로그아웃"):
            logout()
            st.rerun()

        # 학생인 경우 문제 목록 표시
        if st.session_state.user_data["role"] == "student":
            show_student_portal()
        # 교사인 경우 대시보드 표시
        else:
            show_teacher_dashboard()

# 로그인 페이지
def login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 class='main-header'>학원 자동 첨삭 시스템</h1>", unsafe_allow_html=True)
        st.markdown("<p class='info-text'>학생/교사 계정으로 로그인하세요</p>", unsafe_allow_html=True)
        
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        
        if st.button("로그인"):
            if username in users and users[username]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user_data = users[username].copy()
                st.session_state.user_data["username"] = username
                
                # 학생인 경우 문제 로드
                if users[username]["role"] == "student":
                    # 학년에 맞는 문제만 로드
                    grade = users[username]["grade"]
                    if grade == "중2":
                        st.session_state.questions = generate_grade2_questions()
                    elif grade == "중1":
                        # 중1 문제는 여기에 구현 (현재는 빈 리스트로 둠)
                        st.session_state.questions = []
                    elif grade == "중3":
                        # 중3 문제는 여기에 구현 (현재는 빈 리스트로 둠)
                        st.session_state.questions = []
                
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
        
        # 테스트 계정 정보
        st.markdown("---")
        st.markdown("<p class='info-text'>테스트용 계정:</p>", unsafe_allow_html=True)
        st.markdown("""
        - 교사: admin / 1234
        - 학생1: student1 / 1234 (홍길동, 중3)
        - 학생2: student2 / 1234 (김철수, 중2)
        - 학생3: student3 / 1234 (박영희, 중1)
        """)

# 학생 포털
def show_student_portal():
    if not st.session_state.questions:
        st.warning(f"{st.session_state.user_data['grade']} 학년에 해당하는 문제가 아직 준비되지 않았습니다.")
        return
    
    # 문제 인덱스 유효성 검사
    if st.session_state.current_question_index >= len(st.session_state.questions):
        st.session_state.current_question_index = 0
    
    current_q = st.session_state.questions[st.session_state.current_question_index]
    
    # 문제 표시
    st.markdown("<h2 class='sub-header'>문제 목록</h2>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='question-container'>", unsafe_allow_html=True)
    st.write(f"**문제 {st.session_state.current_question_index + 1}/{len(st.session_state.questions)}**")
    st.write(f"**{current_q['content']}**")
    
    # 제출 여부 확인
    submitted_already = st.session_state.submitted and current_q["id"] in st.session_state.answers
    
    # 답안 입력 (다중 선택)
    if current_q["type"] == "multiple_choice":
        options = current_q["options"]
        if not submitted_already:
            selected_option = st.radio("답을 선택하세요:", options, key=f"radio_{current_q['id']}")
            selected_index = options.index(selected_option)
        else:
            selected_index = st.session_state.answers.get(current_q["id"], -1)
            selected_option = options[selected_index] if selected_index >= 0 else "선택 안함"
            st.radio("답을 선택하세요:", options, key=f"radio_submitted_{current_q['id']}", 
                     index=selected_index, disabled=True)
    else:  # 주관식
        if not submitted_already:
            user_answer = st.text_area("답변을 입력하세요:", key=f"textarea_{current_q['id']}", 
                                      height=100)
        else:
            user_answer = st.session_state.answers.get(current_q["id"], "")
            st.text_area("답변을 입력하세요:", value=user_answer, key=f"textarea_submitted_{current_q['id']}", 
                        height=100, disabled=True)
    
    # 채점 결과 표시
    if submitted_already:
        score_info = st.session_state.scores.get(current_q["id"], {})
        score_color = "correct-answer" if score_info.get("is_correct", False) else "wrong-answer"
        
        st.markdown(f"<p class='score-text {score_color}'>점수: {score_info.get('score', 0)}/5</p>", 
                   unsafe_allow_html=True)
        st.markdown(f"<p class='feedback-text'>{score_info.get('feedback', '')}</p>", 
                   unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 네비게이션 및 제출 버튼
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("이전 문제", key="prev_btn", disabled=st.session_state.current_question_index == 0):
            st.session_state.current_question_index = max(0, st.session_state.current_question_index - 1)
            st.rerun()
    
    with col2:
        if st.button("다음 문제", key="next_btn", 
                    disabled=st.session_state.current_question_index == len(st.session_state.questions) - 1):
            st.session_state.current_question_index = min(len(st.session_state.questions) - 1, 
                                                        st.session_state.current_question_index + 1)
            st.rerun()
    
    with col3:
        if not submitted_already:
            if st.button("제출", key="submit_btn"):
                # 답안 저장
                if current_q["type"] == "multiple_choice":
                    st.session_state.answers[current_q["id"]] = selected_index
                    result = grade_answer(current_q, selected_index)
                else:
                    st.session_state.answers[current_q["id"]] = user_answer
                    result = grade_answer(current_q, user_answer)
                
                # 점수 저장
                st.session_state.scores[current_q["id"]] = result
                st.session_state.submitted = True
                st.rerun()
    
    with col4:
        if st.button("전체 결과 보기", key="results_btn", disabled=not st.session_state.submitted):
            st.session_state.view_results = True
    
    # 전체 결과 페이지
    if st.session_state.get("view_results", False) and st.session_state.submitted:
        show_results()

# 결과 페이지
def show_results():
    st.markdown("<h2 class='sub-header'>채점 결과</h2>", unsafe_allow_html=True)
    
    total_score = sum(score_info.get("score", 0) for score_info in st.session_state.scores.values())
    max_possible = len(st.session_state.questions) * 5
    percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
    
    st.markdown(f"<p class='score-text'>총점: {total_score}/{max_possible} ({percentage:.1f}%)</p>", 
               unsafe_allow_html=True)
    
    for i, q in enumerate(st.session_state.questions):
        if q["id"] in st.session_state.scores:
            score_info = st.session_state.scores[q["id"]]
            answer = st.session_state.answers[q["id"]]
            
            if q["type"] == "multiple_choice":
                answer_text = q["options"][answer] if isinstance(answer, int) and answer < len(q["options"]) else "선택 안함"
            else:
                answer_text = answer
            
            score_color = "correct-answer" if score_info.get("is_correct", False) else "wrong-answer"
            
            st.markdown(f"""
            <div class='question-container'>
                <p><strong>문제 {i+1}:</strong> {q['content']}</p>
                <p>제출한 답: {answer_text}</p>
                <p class='{score_color}'>점수: {score_info.get('score', 0)}/5</p>
                <p class='feedback-text'>{score_info.get('feedback', '')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    if st.button("문제로 돌아가기", key="back_to_questions"):
        st.session_state.view_results = False
        st.rerun()

# 교사 대시보드
def show_teacher_dashboard():
    st.markdown("<h2 class='sub-header'>교사 대시보드</h2>", unsafe_allow_html=True)
    
    # 중2 학생 문제 생성 및 확인
    if st.button("중2 문제 생성"):
        st.session_state.questions = generate_grade2_questions()
        st.success("중2 학년용 문제가 생성되었습니다.")
        
        # 구글 시트에 문제 저장
        if USE_GOOGLE_SHEETS:
            try:
                # 기존 문제 삭제
                sheets_api.clear_range('problems!A2:N')
                
                # 새 문제 추가
                problems_data = []
                for q in st.session_state.questions:
                    row = [
                        q["id"],
                        "영어",
                        "중2",
                        "객관식",
                        q["difficulty"],
                        q["content"],
                        q["options"][0],
                        q["options"][1],
                        q["options"][2],
                        q["options"][3],
                        "",  # 보기5
                        q["options"][q["answer"]],  # 정답
                        "time,clock,hour",  # 키워드
                        f"The correct time is {q['options'][q['answer']]}."  # 해설
                    ]
                    problems_data.append(row)
                
                sheets_api.write_range('problems!A2:N21', problems_data)
                st.success("문제가 구글 시트에 저장되었습니다.")
            except Exception as e:
                st.error(f"구글 시트에 문제 저장 오류: {e}")
    
    if st.session_state.questions:
        st.write(f"총 {len(st.session_state.questions)}개의 문제가 생성되었습니다.")
        
        # 문제 목록 표시
        for i, q in enumerate(st.session_state.questions):
            with st.expander(f"문제 {i+1}: {q['content'][:50]}..."):
                st.write(f"**문제:** {q['content']}")
                st.write(f"**유형:** {q['type']}")
                st.write(f"**난이도:** {q['difficulty']}")
                st.write(f"**학년:** 중2")
                
                if q["type"] == "multiple_choice":
                    st.write("**선택지:**")
                    for j, opt in enumerate(q["options"]):
                        if j == q["answer"]:
                            st.markdown(f"- **{opt} (정답)**")
                        else:
                            st.markdown(f"- {opt}")
    
    # 학생 답안 확인
    if USE_GOOGLE_SHEETS:
        st.markdown("---")
        st.subheader("학생 답안 확인")
        
        try:
            student_answers = sheets_api.read_range('student_answers!A2:H')
            if student_answers:
                answers_df = pd.DataFrame(student_answers, columns=[
                    '학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간'
                ])
                st.dataframe(answers_df)
                
                # 평균 점수 계산
                if len(answers_df) > 0 and '점수' in answers_df.columns:
                    try:
                        answers_df['점수'] = pd.to_numeric(answers_df['점수'])
                        avg_score = answers_df['점수'].mean()
                        st.metric("평균 점수", f"{avg_score:.1f}점")
                    except:
                        st.warning("점수 데이터 변환 중 오류가 발생했습니다.")
            else:
                st.info("아직 제출된 학생 답안이 없습니다.")
        except Exception as e:
            st.error(f"학생 답안 불러오기 오류: {e}")

# 앱 실행
if __name__ == "__main__":
    main() 