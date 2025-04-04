import csv
import os
from datetime import datetime

def create_sample_data():
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
            '문제내용': "What time is it? It's ___.",
            '보기1': 'half past six',
            '보기2': 'half to six',
            '보기3': 'six and half',
            '보기4': 'six past half',
            '보기5': '',
            '정답': 'half past six',
            '키워드': 'time,expression,clock',
            '해설': "'Half past six'은 6시 30분을 의미합니다."
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
            '해설': "'I went to school yesterday.'는 과거시제의 올바른 형태입니다. go의 과거형은 went입니다."
        }
    ]
    
    # CSV 파일로 저장
    with open('problems_new.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                     '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for problem in problems:
            writer.writerow(problem)
    
    print(f"총 {len(problems)}개의 샘플 문제가 problems_new.csv 파일로 저장되었습니다.")

if __name__ == "__main__":
    create_sample_data() 