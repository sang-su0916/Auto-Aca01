@echo off
chcp 65001 > nul
title 학원 자동 첨삭 시스템

echo ======= 학원 자동 첨삭 시스템 실행 =======
echo.

echo 데이터 준비 중...

if not exist "sample_questions.csv" (
    echo 문제ID,과목,학년,문제유형,난이도,문제내용,보기1,보기2,보기3,보기4,보기5,정답,키워드,해설 > sample_questions.csv
    echo P001,영어,중3,객관식,중,"What is the capital of the UK?",London,Paris,Berlin,Rome,,London,"capital,UK,London","The capital city of the United Kingdom is London." >> sample_questions.csv
    echo P002,영어,중3,주관식,중,"Write a sentence using the word ""beautiful"".",,,,,,The flower is beautiful.,"beautiful,sentence",주어와 동사를 포함한 완전한 문장이어야 합니다. >> sample_questions.csv
    echo P003,영어,중3,객관식,하,"Which word means ""house""?",home,car,book,pen,,home,"house,home,residence","""home""은 ""house""와 같은 의미로 사용됩니다." >> sample_questions.csv
)

if not exist "student_answers.csv" (
    echo 학생ID,이름,학년,문제ID,제출답안,점수,피드백,제출시간 > student_answers.csv
)

echo 간편 앱 생성 중...
echo import streamlit as st > app_simple.py
echo import pandas as pd >> app_simple.py
echo. >> app_simple.py
echo st.title("학원 자동 첨삭 시스템") >> app_simple.py
echo. >> app_simple.py
echo st.subheader("간편 실행 버전") >> app_simple.py
echo st.write("이 앱은 학생들의 문제 풀이와 자동 채점을 위한 시스템입니다.") >> app_simple.py
echo. >> app_simple.py
echo try: >> app_simple.py
echo     questions = pd.read_csv('sample_questions.csv') >> app_simple.py
echo     st.success(f"{len(questions)}개의 문제가 준비되어 있습니다.") >> app_simple.py
echo     st.dataframe(questions) >> app_simple.py
echo except Exception as e: >> app_simple.py
echo     st.error(f"문제 데이터를 불러오는 중 오류가 발생했습니다: {e}") >> app_simple.py
echo. >> app_simple.py
echo st.write("전체 시스템을 이용하려면 터미널에서 'python -m streamlit run app_without_sheets.py' 명령을 실행해주세요.") >> app_simple.py

echo 앱 실행 중... 잠시 후 브라우저가 자동으로 열립니다.
start explorer "http://localhost:8501"
python -m streamlit run app_simple.py

pause 