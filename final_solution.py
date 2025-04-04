"""
학원 자동 첨삭 시스템 - 최종 솔루션
- pyvenv.cfg 오류 해결
- streamlit 모듈 의존성 제거
- Google API 의존성 제거
"""

import os
import json
import sys
from datetime import datetime

# 샘플 문제 데이터
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

# 학생 답안 데이터
student_answers = []

# 데이터 파일 경로
DATA_DIR = "data"
PROBLEMS_FILE = os.path.join(DATA_DIR, "problems.json")
ANSWERS_FILE = os.path.join(DATA_DIR, "student_answers.json")

def print_welcome():
    """시작 화면을 출력합니다."""
    print("=" * 60)
    print(" " * 12 + "📚 학원 자동 첨삭 시스템 v1.0" + " " * 12)
    print("=" * 60)
    print("\n안내: 이 프로그램은 streamlit 모듈이나 Google API에 의존하지 않는")
    print("콘솔 기반 버전입니다. 가상환경 오류 없이 작동합니다.")
    print("\n기본 기능:")
    print("- 학생: 문제 풀기, 답안 제출, 성적 확인")
    print("- 교사: 문제 관리, 학생 답안 확인, 통계 분석")
    input("\n계속하려면 엔터키를 누르세요...")

# 데이터 디렉토리 생성
def initialize_data():
    """데이터 디렉토리와 파일을 초기화합니다."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # 데이터 로드 시도
    global problems, student_answers
    
    try:
        if os.path.exists(PROBLEMS_FILE):
            with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
                problems = json.load(f)
        
        if os.path.exists(ANSWERS_FILE):
            with open(ANSWERS_FILE, 'r', encoding='utf-8') as f:
                student_answers = json.load(f)
    except Exception as e:
        print(f"데이터 로딩 중 오류: {e}")
        print("기본 샘플 데이터를 사용합니다.")

# 데이터 저장 함수
def save_data():
    """데이터를 JSON 파일로 저장합니다."""
    try:
        with open(PROBLEMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(problems, f, ensure_ascii=False, indent=4)
        
        with open(ANSWERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(student_answers, f, ensure_ascii=False, indent=4)
        
        print("데이터가 저장되었습니다.")
    except Exception as e:
        print(f"데이터 저장 중 오류: {e}")

# 화면 지우기 함수
def clear_screen():
    """콘솔 화면을 지웁니다."""
    os.system('cls' if os.name == 'nt' else 'clear')

# 로그인 함수
def login():
    """사용자 로그인을 처리합니다."""
    clear_screen()
    print("=" * 60)
    print(" " * 20 + "로그인" + " " * 20)
    print("=" * 60)
    print("\n[데모 계정 정보]")
    print("교사 계정: teacher / demo1234")
    print("학생 계정: student / demo5678")
    
    while True:
        username = input("\n아이디: ")
        password = input("비밀번호: ")
        
        if username == "teacher" and password == "demo1234":
            return {
                "user_type": "teacher",
                "user_name": "선생님",
                "user_id": "T001",
                "grade": ""
            }
        elif username == "student" and password == "demo5678":
            return {
                "user_type": "student",
                "user_name": "학생",
                "user_id": "S001",
                "grade": "중3"
            }
        else:
            print("아이디 또는 비밀번호가 잘못되었습니다. 다시 시도하세요.")

# 교사 대시보드
def teacher_dashboard(user_info):
    """교사용 메인 대시보드 화면을 표시합니다."""
    while True:
        clear_screen()
        print("=" * 60)
        print(f" 👨‍🏫 {user_info['user_name']} 대시보드")
        print("=" * 60)
        print("\n[메뉴]")
        print("1. 문제 목록 보기")
        print("2. 새 문제 추가")
        print("3. 학생 답안 확인")
        print("4. 통계 확인")
        print("5. 로그아웃")
        
        choice = input("\n메뉴 선택: ")
        
        if choice == "1":
            view_problems()
        elif choice == "2":
            add_problem()
        elif choice == "3":
            view_student_answers()
        elif choice == "4":
            view_statistics()
        elif choice == "5":
            save_data()
            return
        else:
            input("잘못된 선택입니다. 다시 시도하세요. (계속하려면 엔터)")

# 통계 확인
def view_statistics():
    """학생 답안 통계를 확인합니다."""
    clear_screen()
    print("=" * 60)
    print(" 📊 성적 통계")
    print("=" * 60)
    
    if not student_answers:
        print("\n제출된 답안이 없습니다.")
        input("\n메인 메뉴로 돌아가려면 엔터키를 누르세요.")
        return
    
    # 전체 통계
    total_answers = len(student_answers)
    correct_answers = sum([1 for ans in student_answers if ans['점수'] == 100])
    correct_rate = (correct_answers / total_answers) * 100 if total_answers > 0 else 0
    
    print(f"\n총 제출 답안 수: {total_answers}")
    print(f"정답 수: {correct_answers}")
    print(f"정답률: {correct_rate:.1f}%")
    
    # 과목별 통계
    problem_ids = [ans['문제ID'] for ans in student_answers]
    unique_problem_ids = list(set(problem_ids))
    
    if unique_problem_ids:
        print("\n[문제별 통계]")
        for pid in unique_problem_ids:
            problem_answers = [ans for ans in student_answers if ans['문제ID'] == pid]
            problem_correct = sum([1 for ans in problem_answers if ans['점수'] == 100])
            problem_rate = (problem_correct / len(problem_answers)) * 100 if problem_answers else 0
            
            # 문제 정보 찾기
            problem_info = next((p for p in problems if p['문제ID'] == pid), None)
            problem_title = problem_info['문제내용'][:30] + "..." if problem_info else "알 수 없는 문제"
            
            print(f"\n문제: {pid} - {problem_title}")
            print(f"제출 수: {len(problem_answers)}")
            print(f"정답률: {problem_rate:.1f}%")
    
    input("\n메인 메뉴로 돌아가려면 엔터키를 누르세요.")

# 문제 목록 보기
def view_problems():
    """등록된 모든 문제 목록을 표시합니다."""
    clear_screen()
    print("=" * 60)
    print(" 📝 문제 목록")
    print("=" * 60)
    
    if not problems:
        print("\n등록된 문제가 없습니다.")
    else:
        for i, problem in enumerate(problems):
            print(f"\n[{i+1}] 문제ID: {problem['문제ID']}")
            print(f"과목: {problem['과목']}, 학년: {problem['학년']}, 유형: {problem['문제유형']}, 난이도: {problem['난이도']}")
            print(f"문제: {problem['문제내용']}")
            if problem['문제유형'] == '객관식':
                if problem['보기1']: print(f"① {problem['보기1']}")
                if problem['보기2']: print(f"② {problem['보기2']}")
                if problem['보기3']: print(f"③ {problem['보기3']}")
                if problem['보기4']: print(f"④ {problem['보기4']}")
                if problem['보기5']: print(f"⑤ {problem['보기5']}")
            print(f"정답: {problem['정답']}")
            print(f"해설: {problem['해설']}")
    
    input("\n메인 메뉴로 돌아가려면 엔터키를 누르세요.")

# 새 문제 추가
def add_problem():
    """새로운 문제를 추가합니다."""
    clear_screen()
    print("=" * 60)
    print(" ➕ 새 문제 추가")
    print("=" * 60)
    
    problem_id = f"P{str(len(problems) + 1).zfill(3)}"
    
    subject = input("과목: ")
    while not subject:
        print("과목을 입력해야 합니다.")
        subject = input("과목: ")
    
    grade = input("학년: ")
    while not grade:
        print("학년을 입력해야 합니다.")
        grade = input("학년: ")
    
    problem_type = input("문제유형(객관식/주관식): ")
    while problem_type not in ["객관식", "주관식"]:
        print("문제유형은 '객관식' 또는 '주관식'이어야 합니다.")
        problem_type = input("문제유형(객관식/주관식): ")
    
    difficulty = input("난이도(상/중/하): ")
    while difficulty not in ["상", "중", "하"]:
        print("난이도는 '상', '중', '하' 중 하나여야 합니다.")
        difficulty = input("난이도(상/중/하): ")
    
    content = input("문제내용: ")
    while not content:
        print("문제내용을 입력해야 합니다.")
        content = input("문제내용: ")
    
    options = ["", "", "", "", ""]
    if problem_type == "객관식":
        print("\n객관식 보기를 입력하세요 (최소 2개 이상):")
        options_count = 0
        for i in range(5):
            option = input(f"보기{i+1} (없으면 엔터): ")
            options[i] = option
            if option:
                options_count += 1
        
        if options_count < 2:
            print("객관식 문제는 최소 2개 이상의 보기가 필요합니다.")
            input("다시 시도하려면 엔터키를 누르세요.")
            return
    
    answer = input("정답: ")
    while not answer:
        print("정답을 입력해야 합니다.")
        answer = input("정답: ")
    
    if problem_type == "객관식" and answer not in options:
        print("정답은 입력한 보기 중 하나여야 합니다.")
        input("다시 시도하려면 엔터키를 누르세요.")
        return
    
    keywords = input("키워드(쉼표로 구분): ")
    explanation = input("해설: ")
    
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
    
    problems.append(new_problem)
    save_data()
    
    print(f"\n문제 {problem_id}가 추가되었습니다!")
    input("\n메인 메뉴로 돌아가려면 엔터키를 누르세요.")

# 학생 답안 확인
def view_student_answers():
    """제출된 모든 학생 답안을 확인합니다."""
    clear_screen()
    print("=" * 60)
    print(" 📋 학생 답안 목록")
    print("=" * 60)
    
    if not student_answers:
        print("\n제출된 답안이 없습니다.")
    else:
        for i, answer in enumerate(student_answers):
            print(f"\n[{i+1}] 학생: {answer['이름']} ({answer['학생ID']})")
            print(f"문제ID: {answer['문제ID']}")
            print(f"제출답안: {answer['제출답안']}")
            print(f"점수: {answer['점수']}")
            print(f"피드백: {answer['피드백']}")
            print(f"제출시간: {answer['제출시간']}")
    
    input("\n메인 메뉴로 돌아가려면 엔터키를 누르세요.")

# 학생 포털
def student_portal(user_info):
    """학생용 메인 포털 화면을 표시합니다."""
    while True:
        clear_screen()
        print("=" * 60)
        print(f" 👨‍🎓 {user_info['user_name']} 포털")
        print(f"학년: {user_info['grade']}, 학번: {user_info['user_id']}")
        print("=" * 60)
        print("\n[메뉴]")
        print("1. 문제 풀기")
        print("2. 내 답안 확인")
        print("3. 로그아웃")
        
        choice = input("\n메뉴 선택: ")
        
        if choice == "1":
            solve_problems(user_info)
        elif choice == "2":
            view_my_answers(user_info)
        elif choice == "3":
            save_data()
            return
        else:
            input("잘못된 선택입니다. 다시 시도하세요. (계속하려면 엔터)")

# 문제 풀기
def solve_problems(user_info):
    """문제 목록에서 선택하여 문제를 풉니다."""
    clear_screen()
    print("=" * 60)
    print(" 📝 문제 풀기")
    print("=" * 60)
    
    if not problems:
        print("\n등록된 문제가 없습니다.")
        input("\n메인 메뉴로 돌아가려면 엔터키를 누르세요.")
        return
    
    # 필터링 옵션
    print("\n[필터링 옵션]")
    
    # 과목 필터
    subjects = list(set([p['과목'] for p in problems]))
    print("\n[과목 선택]")
    print("0. 전체")
    for i, subject in enumerate(subjects):
        print(f"{i+1}. {subject}")
    
    subject_choice = input("\n과목 선택(번호): ")
    selected_subject = None
    if subject_choice.isdigit() and int(subject_choice) > 0 and int(subject_choice) <= len(subjects):
        selected_subject = subjects[int(subject_choice)-1]
    
    # 학년 필터
    grades = list(set([p['학년'] for p in problems]))
    print("\n[학년 선택]")
    print("0. 전체")
    for i, grade in enumerate(grades):
        print(f"{i+1}. {grade}")
    
    grade_choice = input("\n학년 선택(번호): ")
    selected_grade = None
    if grade_choice.isdigit() and int(grade_choice) > 0 and int(grade_choice) <= len(grades):
        selected_grade = grades[int(grade_choice)-1]
    
    # 난이도 필터
    difficulties = ["상", "중", "하"]
    print("\n[난이도 선택]")
    print("0. 전체")
    for i, difficulty in enumerate(difficulties):
        print(f"{i+1}. {difficulty}")
    
    difficulty_choice = input("\n난이도 선택(번호): ")
    selected_difficulty = None
    if difficulty_choice.isdigit() and int(difficulty_choice) > 0 and int(difficulty_choice) <= len(difficulties):
        selected_difficulty = difficulties[int(difficulty_choice)-1]
    
    # 필터링 적용
    filtered_problems = problems
    if selected_subject:
        filtered_problems = [p for p in filtered_problems if p['과목'] == selected_subject]
    if selected_grade:
        filtered_problems = [p for p in filtered_problems if p['학년'] == selected_grade]
    if selected_difficulty:
        filtered_problems = [p for p in filtered_problems if p['난이도'] == selected_difficulty]
    
    if not filtered_problems:
        print("\n선택한 조건에 맞는 문제가 없습니다.")
        input("\n메인 메뉴로 돌아가려면 엔터키를 누르세요.")
        return
    
    # 문제 목록 표시
    clear_screen()
    print("=" * 60)
    print(" 📝 문제 목록")
    print("=" * 60)
    
    for i, problem in enumerate(filtered_problems):
        print(f"{i+1}. [{problem['문제유형']}] {problem['과목']} - {problem['문제내용'][:30]}...")
    
    problem_choice = input("\n풀 문제 선택(번호, 0=돌아가기): ")
    
    if problem_choice == "0":
        return
    
    if problem_choice.isdigit() and int(problem_choice) > 0 and int(problem_choice) <= len(filtered_problems):
        selected_problem = filtered_problems[int(problem_choice)-1]
        solve_single_problem(user_info, selected_problem)
    else:
        input("잘못된 선택입니다. 메인 메뉴로 돌아가려면 엔터키를 누르세요.")

# 단일 문제 풀기
def solve_single_problem(user_info, problem):
    """선택한 문제를 풀고 답안을 제출합니다."""
    clear_screen()
    print("=" * 60)
    print(f" 📝 문제: {problem['문제ID']}")
    print("=" * 60)
    
    print(f"\n[과목: {problem['과목']}, 학년: {problem['학년']}, 난이도: {problem['난이도']}]")
    print(f"\n{problem['문제내용']}")
    
    answer = ""
    if problem['문제유형'] == '객관식':
        options = []
        if problem['보기1']: options.append(problem['보기1'])
        if problem['보기2']: options.append(problem['보기2'])
        if problem['보기3']: options.append(problem['보기3'])
        if problem['보기4']: options.append(problem['보기4'])
        if problem['보기5']: options.append(problem['보기5'])
        
        print("\n[보기]")
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        
        while True:
            answer_input = input("\n정답 번호 입력 (0=취소): ")
            if answer_input == "0":
                return
            
            if answer_input.isdigit() and int(answer_input) > 0 and int(answer_input) <= len(options):
                answer = options[int(answer_input)-1]
                break
            else:
                print("잘못된 입력입니다. 다시 시도하세요.")
    else:
        print("\n주관식 문제입니다. 답안을 작성하세요.")
        while True:
            answer = input("\n답안 작성 (취소하려면 '취소' 입력): ")
            if answer.lower() == "취소":
                return
            if answer:
                break
            print("답안을 입력해야 합니다.")
    
    # 점수 계산
    score = 100 if answer == problem['정답'] else 0
    feedback = "정답입니다!" if score == 100 else f"오답입니다. 정답은 {problem['정답']}입니다."
    
    # 답안 저장
    submission = {
        '학생ID': user_info['user_id'],
        '이름': user_info['user_name'],
        '학년': user_info['grade'],
        '문제ID': problem['문제ID'],
        '제출답안': answer,
        '점수': score,
        '피드백': feedback,
        '제출시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    student_answers.append(submission)
    save_data()
    
    # 결과 표시
    clear_screen()
    print("=" * 60)
    print(" 📋 채점 결과")
    print("=" * 60)
    
    print(f"\n문제: {problem['문제내용']}")
    print(f"제출답안: {answer}")
    
    if score == 100:
        print("\n✅ 정답입니다!")
    else:
        print("\n❌ 오답입니다.")
        print(f"정답: {problem['정답']}")
        print(f"해설: {problem['해설']}")
    
    input("\n계속하려면 엔터키를 누르세요.")

# 내 답안 확인
def view_my_answers(user_info):
    """학생 자신의 제출 답안을 확인합니다."""
    clear_screen()
    print("=" * 60)
    print(" 📊 내 답안 목록")
    print("=" * 60)
    
    my_answers = [ans for ans in student_answers if ans['학생ID'] == user_info['user_id']]
    
    if not my_answers:
        print("\n제출한 답안이 없습니다.")
    else:
        for i, answer in enumerate(my_answers):
            # 문제 정보 찾기
            problem_info = next((p for p in problems if p['문제ID'] == answer['문제ID']), None)
            problem_title = problem_info['문제내용'][:30] + "..." if problem_info else "알 수 없는 문제"
            
            print(f"\n[{i+1}] 문제: {problem_title}")
            print(f"문제ID: {answer['문제ID']}")
            print(f"제출답안: {answer['제출답안']}")
            print(f"점수: {answer['점수']}")
            print(f"피드백: {answer['피드백']}")
            print(f"제출시간: {answer['제출시간']}")
        
        # 통계 표시
        total_score = sum([ans['점수'] for ans in my_answers])
        avg_score = total_score / len(my_answers)
        correct_count = sum([1 for ans in my_answers if ans['점수'] == 100])
        correct_rate = (correct_count / len(my_answers)) * 100
        
        print("\n[통계]")
        print(f"평균 점수: {avg_score:.1f}점")
        print(f"정답률: {correct_rate:.1f}%")
        print(f"총 제출 답안 수: {len(my_answers)}")
    
    input("\n메인 메뉴로 돌아가려면 엔터키를 누르세요.")

# 메인 함수
def main():
    # 시작 화면 출력
    print_welcome()
    
    # 데이터 초기화
    initialize_data()
    
    try:
        while True:
            clear_screen()
            # 로그인
            user_info = login()
            
            # 사용자 타입에 따라 대시보드 표시
            if user_info["user_type"] == "teacher":
                teacher_dashboard(user_info)
            else:
                student_portal(user_info)
            
            # 재시작 여부 확인
            clear_screen()
            print("=" * 60)
            print(" 🔄 세션 종료")
            print("=" * 60)
            restart = input("\n다시 로그인하시겠습니까? (y/n): ")
            if restart.lower() != 'y':
                break
    
    except KeyboardInterrupt:
        print("\n\n프로그램이 강제 종료되었습니다.")
    except Exception as e:
        print(f"\n\n오류 발생: {e}")
    finally:
        clear_screen()
        print("=" * 60)
        print(" 👋 학원 자동 첨삭 시스템을 종료합니다.")
        print("=" * 60)
        print("\n데이터가 저장되었습니다.")
        print("이용해 주셔서 감사합니다!")

if __name__ == "__main__":
    main() 