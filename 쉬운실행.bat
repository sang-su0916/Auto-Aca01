@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ======= 학원 자동 첨삭 시스템 쉬운 실행 =======
echo.

:: Python 설치 확인
echo 1. Python 설치 확인 중...
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python이 설치되어 있지 않습니다.
        echo Python 공식 사이트에서 설치해주세요: https://www.python.org/downloads/
        echo 설치 시 "Add Python to PATH" 옵션을 체크해주세요.
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)
echo [OK] Python 설치 확인 완료

:: 필요한 패키지 설치
echo 2. 필요한 패키지 설치 중... (약간의 시간이 소요될 수 있습니다)
%PYTHON_CMD% -m pip install streamlit pandas -q
echo [OK] 패키지 설치 완료

:: 샘플 데이터 준비
echo 3. 샘플 데이터 준비 중...
if not exist "sample_questions.csv" (
    echo 문제ID,과목,학년,문제유형,난이도,문제내용,보기1,보기2,보기3,보기4,보기5,정답,키워드,해설 > sample_questions.csv
    echo P001,영어,중3,객관식,중,"What is the capital of the UK?",London,Paris,Berlin,Rome,,London,"capital,UK,London","The capital city of the United Kingdom is London." >> sample_questions.csv
    echo P002,영어,중3,주관식,중,"Write a sentence using the word ""beautiful"".",,,,,,The flower is beautiful.,"beautiful,sentence",주어와 동사를 포함한 완전한 문장이어야 합니다. >> sample_questions.csv
    echo P003,영어,중3,객관식,하,"Which word means ""house""?",home,car,book,pen,,home,"house,home,residence","""home""은 ""house""와 같은 의미로 사용됩니다." >> sample_questions.csv
    echo [OK] 샘플 문제 데이터 생성 완료
) else (
    echo [OK] 기존 문제 데이터 사용
)

if not exist "student_answers.csv" (
    echo 학생ID,이름,학년,문제ID,제출답안,점수,피드백,제출시간 > student_answers.csv
    echo [OK] 학생 답안 데이터 파일 생성 완료
) else (
    echo [OK] 기존 학생 답안 데이터 사용
)

:: 앱 시작
echo 4. 앱 시작 준비 중... 잠시 후 웹 브라우저가 자동으로 열립니다.

:: 브라우저 자동 실행을 위한 임시 Python 스크립트 생성
echo import time, webbrowser > open_browser.py
echo time.sleep(3) >> open_browser.py
echo webbrowser.open("http://localhost:8501") >> open_browser.py

start %PYTHON_CMD% open_browser.py
%PYTHON_CMD% -m streamlit run app_without_sheets.py

:: 임시 파일 삭제
del open_browser.py

pause 