import csv
import pandas as pd
import os
from datetime import datetime

def create_and_save_sample_data():
    """샘플 문제 데이터를 생성하고 CSV 파일로 저장합니다."""
    
    print("샘플 영어 문제 데이터를 생성합니다...")
    
    # 샘플 데이터 정의
    problems = [
        {
            '문제ID': 'P001',
            '과목': '영어',
            '학년': '중1',
            '문제유형': '객관식',
            '난이도': '하',
            '문제내용': 'Which of the following is a fruit?',
            '보기1': 'Apple',
            '보기2': 'Book',
            '보기3': 'Pencil',
            '보기4': 'Chair',
            '보기5': '',
            '정답': 'Apple',
            '키워드': 'fruit,apple,vocabulary',
            '해설': 'Apple(사과)은 과일입니다. 나머지는 과일이 아닙니다.'
        },
        {
            '문제ID': 'P002',
            '과목': '영어',
            '학년': '중1',
            '문제유형': '객관식',
            '난이도': '하',
            '문제내용': 'Choose the correct subject pronoun: ___ is my friend.',
            '보기1': 'He',
            '보기2': 'Him',
            '보기3': 'His',
            '보기4': 'Himself',
            '보기5': '',
            '정답': 'He',
            '키워드': 'pronoun,subject pronoun,grammar',
            '해설': 'He는 주격 대명사입니다. Him(목적격), His(소유격), Himself(재귀대명사)는 주격 대명사가 아닙니다.'
        },
        {
            '문제ID': 'P003',
            '과목': '영어',
            '학년': '중2',
            '문제유형': '객관식',
            '난이도': '중',
            '문제내용': 'What time is it? It\'s ___.',
            '보기1': 'half past six',
            '보기2': 'half to six',
            '보기3': 'six and half',
            '보기4': 'six past half',
            '보기5': '',
            '정답': 'half past six',
            '키워드': 'time,expression,clock',
            '해설': '\'Half past six\'은 6시 30분을 의미합니다.'
        },
        {
            '문제ID': 'P004',
            '과목': '영어',
            '학년': '중2',
            '문제유형': '객관식',
            '난이도': '중',
            '문제내용': 'Which word is a verb?',
            '보기1': 'Run',
            '보기2': 'Table',
            '보기3': 'Beautiful',
            '보기4': 'Happy',
            '보기5': '',
            '정답': 'Run',
            '키워드': 'verb,part of speech,grammar',
            '해설': 'Run(달리다)은 동사입니다. Table(명사), Beautiful(형용사), Happy(형용사)는 동사가 아닙니다.'
        },
        {
            '문제ID': 'P005',
            '과목': '영어',
            '학년': '중3',
            '문제유형': '객관식',
            '난이도': '중',
            '문제내용': 'Choose the correct sentence.',
            '보기1': 'I went to school yesterday.',
            '보기2': 'I go to school yesterday.',
            '보기3': 'I goed to school yesterday.',
            '보기4': 'I gone to school yesterday.',
            '보기5': '',
            '정답': 'I went to school yesterday.',
            '키워드': 'past tense,grammar,verb form',
            '해설': '\'I went to school yesterday.\'는 과거시제의 올바른 형태입니다. go의 과거형은 went입니다.'
        },
        {
            '문제ID': 'P006',
            '과목': '영어',
            '학년': '중3',
            '문제유형': '주관식',
            '난이도': '중',
            '문제내용': 'Write a sentence using the word \'beautiful\'.',
            '보기1': 'The flower is beautiful.',
            '보기2': '',
            '보기3': '',
            '보기4': '',
            '보기5': '',
            '정답': 'The flower is beautiful.',
            '키워드': 'sentence writing,adjective,vocabulary',
            '해설': '\'beautiful\'을 사용한 완전한 문장을 작성해야 합니다. 주어, 동사가 포함되어야 합니다.'
        },
        {
            '문제ID': 'P007',
            '과목': '영어',
            '학년': '고1',
            '문제유형': '객관식',
            '난이도': '중',
            '문제내용': 'Choose the correct form: He ___ football now.',
            '보기1': 'is playing',
            '보기2': 'plays',
            '보기3': 'play',
            '보기4': 'playing',
            '보기5': '',
            '정답': 'is playing',
            '키워드': 'present continuous,grammar,tense',
            '해설': '현재 진행형(be동사 + -ing)은 현재 일어나고 있는 행동을 표현할 때 사용합니다.'
        },
        {
            '문제ID': 'P008',
            '과목': '영어',
            '학년': '고1',
            '문제유형': '주관식',
            '난이도': '중',
            '문제내용': 'What is the capital of the UK?',
            '보기1': 'London',
            '보기2': '',
            '보기3': '',
            '보기4': '',
            '보기5': '',
            '정답': 'London',
            '키워드': 'capital,UK,geography',
            '해설': '영국(UK)의 수도는 런던(London)입니다.'
        },
        {
            '문제ID': 'P009',
            '과목': '영어',
            '학년': '고2',
            '문제유형': '객관식',
            '난이도': '상',
            '문제내용': 'Choose the sentence in the passive voice.',
            '보기1': 'The letter was written by John.',
            '보기2': 'John wrote the letter.',
            '보기3': 'John is writing the letter.',
            '보기4': 'John will write the letter.',
            '보기5': '',
            '정답': 'The letter was written by John.',
            '키워드': 'passive voice,grammar,sentence structure',
            '해설': '수동태는 \'be동사 + 과거분사(p.p)\'의 형태입니다. \'The letter was written by John\'이 수동태 문장입니다.'
        },
        {
            '문제ID': 'P010',
            '과목': '영어',
            '학년': '고2',
            '문제유형': '주관식',
            '난이도': '상',
            '문제내용': 'What does \'procrastination\' mean?',
            '보기1': 'Delaying or postponing tasks',
            '보기2': '',
            '보기3': '',
            '보기4': '',
            '보기5': '',
            '정답': 'Delaying or postponing tasks',
            '키워드': 'vocabulary,meaning,definition',
            '해설': '\'procrastination\'은 \'일이나 과제를 미루는 것\'을 의미합니다.'
        }
    ]
    
    # 학생 답안 데이터 구조 정의
    student_answers = []
    
    # 데이터프레임으로 변환
    problems_df = pd.DataFrame(problems)
    student_answers_df = pd.DataFrame(student_answers, columns=[
        '학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간'
    ])
    
    # CSV 파일로 저장
    problems_df.to_csv('problems.csv', index=False, encoding='utf-8-sig')
    student_answers_df.to_csv('student_answers.csv', index=False, encoding='utf-8-sig')
    
    print(f"총 {len(problems)}개의 샘플 문제가 problems.csv 파일로 저장되었습니다.")
    print("student_answers.csv 파일도 생성되었습니다.")
    
    # Excel 파일로도 저장
    try:
        with pd.ExcelWriter('english_problems.xlsx') as writer:
            problems_df.to_excel(writer, sheet_name='problems', index=False)
            student_answers_df.to_excel(writer, sheet_name='student_answers', index=False)
        print("Excel 파일(english_problems.xlsx)로도 저장되었습니다.")
    except Exception as e:
        print(f"Excel 파일 저장 중 오류가 발생했습니다: {str(e)}")
        print("openpyxl 패키지가 설치되어 있지 않을 수 있습니다. 'pip install openpyxl'로 설치해보세요.")

if __name__ == "__main__":
    create_and_save_sample_data() 