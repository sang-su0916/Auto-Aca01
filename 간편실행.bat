@echo off
chcp 65001 > nul
title 학원 자동 첨삭 시스템

echo ===== 학원 자동 첨삭 시스템 =====
echo.

:: Python 설치 확인
where py >nul 2>nul
if %errorlevel% neq 0 (
  echo Python이 설치되어 있지 않습니다.
  echo https://www.python.org/downloads/ 에서 Python을 설치한 후 다시 실행해주세요.
  pause
  exit /b
) else (
  set PYTHON=py
  echo Python 확인 완료!
)

:: 데이터 파일 생성
if not exist "sample_questions.csv" (
  echo 샘플 문제 파일 생성 중...
  echo 문제ID,과목,학년,문제유형,난이도,문제내용,보기1,보기2,보기3,보기4,보기5,정답,키워드,해설 > sample_questions.csv
  echo P001,영어,중3,객관식,중,"What is the capital of the UK?",London,Paris,Berlin,Rome,,London,"capital,UK,London","The capital city of the United Kingdom is London." >> sample_questions.csv
  echo P002,영어,중3,주관식,중,"Write a sentence using the word ""beautiful"".",,,,,,The flower is beautiful.,"beautiful,sentence",주어와 동사를 포함한 완전한 문장이어야 합니다. >> sample_questions.csv
  echo P003,영어,중3,객관식,하,"Which word means ""house""?",home,car,book,pen,,home,"house,home,residence","""home""은 ""house""와 같은 의미로 사용됩니다." >> sample_questions.csv
)

if not exist "student_answers.csv" (
  echo 학생 답변 파일 생성 중...
  echo 학생ID,이름,학년,문제ID,제출답안,점수,피드백,제출시간 > student_answers.csv
)

:: 간단 실행 앱 생성
echo 앱 파일 생성 중...
(
echo import streamlit as st
echo import pandas as pd
echo import os
echo from datetime import datetime
echo.
echo st.set_page_config(page_title="학원 자동 첨삭 시스템", page_icon="📚")
echo st.title("📚 학원 자동 첨삭 시스템")
echo.
echo try:
echo     problems = pd.read_csv("sample_questions.csv")
echo     st.write("등록된 문제 목록:")
echo     st.dataframe(problems)
echo     st.success(f"{len(problems)}개의 문제가 준비되었습니다.")
echo except Exception as e:
echo     st.error(f"문제 데이터를 불러오는 중 오류가 발생했습니다: {e}")
echo.
echo try:
echo     answers = pd.read_csv("student_answers.csv")
echo     if not answers.empty:
echo         st.write("제출된 답안:")
echo         st.dataframe(answers)
echo except Exception as e:
echo     st.write("아직 제출된 답안이 없습니다.")
echo.
echo st.subheader("학생 로그인")
echo.
echo name = st.text_input("이름")
echo student_id = st.text_input("학번")
echo grade = st.selectbox("학년", ["중1", "중2", "중3", "고1", "고2", "고3"])
echo.
echo if st.button("문제 풀기"):
echo     if name and student_id:
echo         st.success(f"{name} 학생 로그인 성공!")
echo         st.session_state.name = name
echo         st.session_state.student_id = student_id
echo         st.session_state.grade = grade
echo         st.rerun()
echo     else:
echo         st.error("이름과 학번을 입력해주세요")
) > simple_app.py

echo 앱을 시작합니다. 잠시 기다려주세요...
start explorer "http://localhost:8501"
py -m streamlit run simple_app.py

echo.
pause 