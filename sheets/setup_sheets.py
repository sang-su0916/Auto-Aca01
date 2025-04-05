import gspread
import os
import pandas as pd
import logging
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import time
from googleapiclient.discovery import build
from sheets.google_sheets import GoogleSheetsAPI  # GoogleSheetsAPI 클래스 가져오기

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경 변수 관련 설정
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("dotenv 모듈을 찾을 수 없습니다. 환경 변수는 직접 설정된 값을 사용합니다.")

# 스프레드시트 ID 설정
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
if not SPREADSHEET_ID:
    SPREADSHEET_ID = "1YcKaHcjnx5-WypEpYbcfg04s8TIq280l-gi6iISF5NQ"
    logger.info(f"환경 변수에서 스프레드시트 ID를 찾을 수 없어 기본값을 사용합니다: {SPREADSHEET_ID}")

class GoogleSheetsSetup:
    def __init__(self):
        """Initialize Google Sheets API with credentials"""
        if not DOTENV_AVAILABLE:
            logger.warning("dotenv 모듈을 사용할 수 없습니다. 환경 변수는 직접 설정된 값을 사용합니다.")
        
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SERVICE_ACCOUNT_FILE = 'credentials.json'
        self.SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        
        if not self.SPREADSHEET_ID:
            self.SPREADSHEET_ID = "1YcKaHcjnx5-WypEpYbcfg04s8TIq280l-gi6iISF5NQ"
            logger.info(f"Google Sheets ID: {self.SPREADSHEET_ID}")
        
        try:
            self.service = self._get_google_sheets_service()
            logger.info("Google Sheets API 서비스 생성 성공")
        except Exception as e:
            logger.error(f"Google Sheets API 서비스 생성 실패: {str(e)}")
            self.service = None
    
    def _get_google_sheets_service(self):
        """Google Sheets API 서비스 객체 생성"""
        credentials = Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        return service
    
    def initialize_sheets(self):
        """시트 초기화 및 헤더 설정"""
        if not self.service:
            logger.error("Google Sheets API 서비스가 초기화되지 않았습니다.")
            return False
        
        try:
            # problems 시트 헤더 설정
            problems_headers = [
                ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                 '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
            ]
            
            # student_answers 시트 헤더 설정
            student_answers_headers = [
                ['학생ID', '이름', '학년', '문제ID', '제출답안', '점수', '피드백', '제출시간']
            ]
            
            # 헤더 업데이트
            self.update_values('problems!A1:N1', problems_headers)
            logger.info("problems 시트 헤더 설정 완료")
            
            self.update_values('student_answers!A1:H1', student_answers_headers)
            logger.info("student_answers 시트 헤더 설정 완료")
            
            # 샘플 문제 추가
            self.add_sample_problems()
            
            return True
        except Exception as e:
            logger.error(f"스프레드시트 설정 중 오류 발생: {str(e)}")
            return False
    
    def update_values(self, range_name, values):
        """Update values in the specified range"""
        body = {'values': values}
        self.service.spreadsheets().values().update(
            spreadsheetId=self.SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
    
    def add_sample_problems(self):
        """Add sample problems to the problems sheet"""
        # 초등학교 문제 (문법 유형)
        elementary_grammar_problems = [
            ['P101', '영어', '초6', '객관식', '하', '다음 중 "be동사"가 있는 문장은?', 
             'I have a pen.', 'She is a student.', 'They go to school.', 'We like pizza.', '', 
             'She is a student.', 'grammar,be verb', 'is가 be동사입니다.'],
            
            ['P102', '영어', '초6', '객관식', '하', '다음 중 복수형이 옳은 것은?', 
             'child → childs', 'box → boxs', 'baby → babys', 'book → books', '', 
             'book → books', 'grammar,plural', '일반적인 명사의 복수형은 -s를 붙입니다.'],
            
            ['P103', '영어', '초5', '객관식', '하', '"I ___ a student."에 들어갈 말로 알맞은 것은?', 
             'am', 'is', 'are', 'be', '', 
             'am', 'grammar,be verb', 'I와 함께 쓰는 be동사는 am입니다.'],
            
            ['P104', '영어', '초5', '객관식', '중', '현재진행형에 관한 설명으로 맞는 것은?', 
             'will + 동사원형', '동사원형 + s', 'be동사 + 동사원형', 'be동사 + 동사ing', '', 
             'be동사 + 동사ing', 'grammar,present continuous', '현재진행형은 be동사 + 동사ing 형태로 만듭니다.'],
            
            ['P105', '영어', '초6', '주관식', '중', '"그녀는 지금 책을 읽고 있다"를 영어로 쓰시오.',
             '', '', '', '', '', 
             'She is reading a book.', 'grammar,present continuous,translation', '현재진행형(be동사 + 동사ing)을 사용한 영어 문장입니다.']
        ]
        
        # 초등학교 문제 (어휘 유형)
        elementary_vocabulary_problems = [
            ['P106', '영어', '초5', '객관식', '하', '다음 중 "과일"이 아닌 것은?', 
             'apple', 'orange', 'banana', 'potato', '', 
             'potato', 'vocabulary,fruits,vegetables', 'potato(감자)는 채소(vegetable)입니다.'],
            
            ['P107', '영어', '초5', '객관식', '하', '"red"의 뜻으로 알맞은 것은?', 
             '파랑', '초록', '빨강', '노랑', '', 
             '빨강', 'vocabulary,colors', 'red는 빨강(색)을 의미합니다.'],
            
            ['P108', '영어', '초6', '객관식', '하', '"동물"을 뜻하는 영어 단어는?', 
             'animal', 'plant', 'mineral', 'vegetable', '', 
             'animal', 'vocabulary,categories', 'animal은 동물을 의미합니다.'],
            
            ['P109', '영어', '초5', '주관식', '중', '"사과"를 영어로 쓰시오.',
             '', '', '', '', '', 
             'apple', 'vocabulary,fruits', 'apple은 사과를 의미합니다.'],
            
            ['P110', '영어', '초6', '주관식', '중', '다음 중 "개, 고양이, 말"을 모두 포함하는 범주는?',
             '', '', '', '', '', 
             'animals', 'vocabulary,categories', 'dog(개), cat(고양이), horse(말)는 모두 animals(동물) 범주에 속합니다.']
        ]
        
        # 중학교 문제 (문법 유형)
        middle_grammar_problems = [
            ['P201', '영어', '중1', '객관식', '중', '과거시제에 대한 설명으로 옳은 것은?', 
             '미래에 일어날 일을 표현한다.', '현재 진행 중인 일을 표현한다.', '과거에 일어난 일을 표현한다.', '항상 하는 일을 표현한다.', '', 
             '과거에 일어난 일을 표현한다.', 'grammar,past tense', '과거시제는 과거에 일어난 일을 표현합니다.'],
            
            ['P202', '영어', '중2', '객관식', '중', '다음 중 현재완료형은?', 
             'I went to school.', 'I go to school.', 'I have gone to school.', 'I will go to school.', '', 
             'I have gone to school.', 'grammar,present perfect', '현재완료형은 have/has + 과거분사 형태로 만듭니다.'],
            
            ['P203', '영어', '중3', '객관식', '상', '조건문에 대한 설명으로 옳지 않은 것은?', 
             'If절에는 미래시제가 올 수 없다.', 'If I were you는 가정법 과거이다.', 'If절 뒤에는 항상 will이 온다.', '조건문은 if로 시작한다.', '', 
             'If절 뒤에는 항상 will이 온다.', 'grammar,conditionals', 'If절 뒤에는 상황에 따라 다양한 시제가 올 수 있습니다.'],
            
            ['P204', '영어', '중1', '주관식', '중', '"그는 어제 학교에 갔다"를 영어로 쓰시오.',
             '', '', '', '', '', 
             'He went to school yesterday.', 'grammar,past tense,translation', '과거시제 문장으로, went는 go의 과거형입니다.'],
            
            ['P205', '영어', '중2', '주관식', '상', '"If I ___ rich, I would buy a house."에서 빈칸에 들어갈 말은?',
             '', '', '', '', '', 
             'were', 'grammar,conditionals,subjunctive', '가정법 과거에서는 I, he, she와 함께 were를 사용합니다.']
        ]
        
        # 중학교 문제 (어휘 유형)
        middle_vocabulary_problems = [
            ['P206', '영어', '중1', '객관식', '중', '"공부하다"의 의미를 가진 단어는?', 
             'play', 'read', 'study', 'write', '', 
             'study', 'vocabulary,verbs', 'study는 공부하다라는 의미의 동사입니다.'],
            
            ['P207', '영어', '중2', '객관식', '중', '다음 중 "직업"을 나타내는 단어가 아닌 것은?', 
             'teacher', 'doctor', 'student', 'river', '', 
             'river', 'vocabulary,occupations', 'river(강)은 직업이 아닌 자연물입니다.'],
            
            ['P208', '영어', '중3', '객관식', '상', '"tremendous"의 의미와 가장 가까운 것은?', 
             'tiny', 'huge', 'sad', 'funny', '', 
             'huge', 'vocabulary,adjectives,synonyms', 'tremendous는 엄청난, 거대한이라는 의미로 huge(거대한)와 의미가 가장 유사합니다.'],
            
            ['P209', '영어', '중1', '주관식', '중', '영어로 "1부터 5까지" 숫자를 순서대로 쓰시오.',
             '', '', '', '', '', 
             'one, two, three, four, five', 'vocabulary,numbers', '영어 기수는 one, two, three, four, five입니다.'],
            
            ['P210', '영어', '중2', '주관식', '상', '"기쁘다"의 반대말을 영어로 쓰시오.',
             '', '', '', '', '', 
             'sad', 'vocabulary,antonyms,emotions', 'happy(기쁘다)의 반대말은 sad(슬프다)입니다.']
        ]
        
        # 중학교 문제 (독해 유형)
        middle_reading_problems = [
            ['P211', '영어', '중1', '객관식', '중', 
             'Tom likes playing soccer. He plays soccer every day after school. He wants to be a soccer player in the future. What does Tom like?', 
             'baseball', 'soccer', 'tennis', 'swimming', '', 
             'soccer', 'reading,comprehension', '지문에서 "Tom likes playing soccer"라고 명시되어 있습니다.'],
            
            ['P212', '영어', '중2', '객관식', '중', 
             'Mary gets up at 6:30 in the morning. She goes to school at 8:00. She eats lunch at 12:30. She comes home at 4:00. When does Mary go to school?', 
             '6:30', '8:00', '12:30', '4:00', '', 
             '8:00', 'reading,comprehension,time', '지문에서 "She goes to school at 8:00"이라고 명시되어 있습니다.'],
            
            ['P213', '영어', '중3', '객관식', '상', 
             'The Earth is the third planet from the Sun. It is the only planet known to have life. About 71% of the Earth\'s surface is covered with water. What percentage of the Earth\'s surface is covered with water?', 
             '31%', '51%', '71%', '91%', '', 
             '71%', 'reading,comprehension,numbers', '지문에서 "About 71% of the Earth\'s surface is covered with water"라고 명시되어 있습니다.'],
            
            ['P214', '영어', '중2', '주관식', '상', 
             'John is taller than Mike. Mike is taller than Tom. Who is the shortest?', 
             '', '', '', '', '', 
             'Tom', 'reading,comprehension,comparison', 'John > Mike > Tom 순으로 키가 큽니다. 따라서 Tom이 가장 작습니다.'],
            
            ['P215', '영어', '중3', '주관식', '상', 
             'The library opens at 9:00 AM and closes at 6:00 PM from Monday to Friday. On weekends, it opens at 10:00 AM and closes at 4:00 PM. What time does the library close on Saturday?', 
             '', '', '', '', '', 
             '4:00 PM', 'reading,comprehension,time', '지문에 따르면 주말(weekends)에는 오후 4시(4:00 PM)에 도서관이 닫습니다.']
        ]
        
        # 고등학교 문제 (문법 유형)
        high_grammar_problems = [
            ['P301', '영어', '고1', '객관식', '상', '다음 중 관계대명사의 쓰임이 옳지 않은 것은?', 
             'The man who is talking to her is my father.', 'The book which I read yesterday was interesting.', 
             'The city where I lived was beautiful.', 'The reason because he left is unclear.', '', 
             'The reason because he left is unclear.', 'grammar,relative pronouns', '"The reason why he left" 또는 "The reason that he left"가 올바른 표현입니다.'],
            
            ['P302', '영어', '고2', '객관식', '상', '다음 문장의 틀린 부분은? "She has lived in London since five years."', 
             'She has', 'lived in', 'London since', 'five years', '', 
             'five years', 'grammar,present perfect,prepositions', 'since는 시점을 나타내므로 "since 2018" 또는 "for five years"가 올바른 표현입니다.'],
            
            ['P303', '영어', '고3', '객관식', '상', '다음 중 수동태로 옳은 것은?', 
             'The news was telling by the reporter.', 'The book has written by the author.', 
             'The house is being built by the workers.', 'The letter had wrote by my friend.', '', 
             'The house is being built by the workers.', 'grammar,passive voice', '수동태는 be동사 + 과거분사 형태로 만듭니다. "is being built"는 현재진행형 수동태입니다.'],
            
            ['P304', '영어', '고1', '주관식', '상', '"그가 집에 도착했을 때 비가 내리고 있었다"를 영어로 쓰시오.',
             '', '', '', '', '', 
             'It was raining when he arrived home.', 'grammar,past continuous,translation', '과거진행형(was/were + 동사ing)을 사용한 영어 문장입니다.'],
            
            ['P305', '영어', '고2', '주관식', '상', '"Had I known the truth, I would have told you."와 같은 의미의 문장을 If로 시작하여 쓰시오.',
             '', '', '', '', '', 
             'If I had known the truth, I would have told you.', 'grammar,conditionals,past perfect', '가정법 과거완료 문장으로, 과거의 사실과 반대되는 상황을 가정합니다.']
        ]
        
        # 고등학교 문제 (어휘 유형)
        high_vocabulary_problems = [
            ['P306', '영어', '고1', '객관식', '상', '"notorious"의 의미와 가장 가까운 것은?', 
             'famous for good things', 'famous for bad things', 'unknown', 'popular', '', 
             'famous for bad things', 'vocabulary,adjectives', 'notorious는 악명 높은, 나쁜 평판이 있는이라는 의미입니다.'],
            
            ['P307', '영어', '고2', '객관식', '상', '다음 중 "resilience"의 의미로 가장 적절한 것은?', 
             'the ability to recover quickly from difficulties', 'the state of being very angry', 
             'the act of giving up easily', 'the quality of being very strict', '', 
             'the ability to recover quickly from difficulties', 'vocabulary,abstract nouns', 'resilience는 회복력, 탄력성을 의미합니다.'],
            
            ['P308', '영어', '고3', '객관식', '상', '다음 중 "ambiguous"와 의미가 반대되는 단어는?', 
             'clear', 'vague', 'confusing', 'doubtful', '', 
             'clear', 'vocabulary,antonyms', 'ambiguous(모호한)의 반대말은 clear(명확한)입니다.'],
            
            ['P309', '영어', '고1', '주관식', '상', '"procrastination"의 의미를 한 문장으로 설명하시오.',
             '', '', '', '', '', 
             'the act of delaying or postponing tasks', 'vocabulary,definitions', 'procrastination은 일이나 활동을 미루는 행동을 의미합니다.'],
            
            ['P310', '영어', '고2', '주관식', '상', '"benevolent"와 "malevolent"의 관계와 같은 관계의 단어 쌍을 쓰시오.',
             '', '', '', '', '', 
             'optimistic and pessimistic', 'vocabulary,antonyms,relationships', 'benevolent(자비로운)와 malevolent(악의적인)는 반의어 관계입니다. optimistic(낙관적인)과 pessimistic(비관적인)도 반의어 관계입니다.']
        ]
        
        # 고등학교 문제 (독해 유형)
        high_reading_problems = [
            ['P311', '영어', '고1', '객관식', '상', 
             'Renewable energy sources such as solar and wind power are becoming increasingly important as we face climate change. Unlike fossil fuels, these energy sources do not produce greenhouse gases. According to the passage, what is an advantage of renewable energy sources?', 
             'They are cheaper than fossil fuels.', 'They do not produce greenhouse gases.', 
             'They are more widely available.', 'They are easier to transport.', '', 
             'They do not produce greenhouse gases.', 'reading,comprehension,environment', '지문에서 "Unlike fossil fuels, these energy sources do not produce greenhouse gases"라고 명시되어 있습니다.'],
            
            ['P312', '영어', '고2', '객관식', '상', 
             'The human brain is the most complex organ in the body. It contains approximately 86 billion neurons. These neurons communicate through synapses, creating complex networks. The brain consumes about 20% of the body\'s energy despite making up only 2% of its weight. What percentage of the body\'s energy does the brain consume?', 
             '2%', '10%', '20%', '86%', '', 
             '20%', 'reading,comprehension,biology', '지문에서 "The brain consumes about 20% of the body\'s energy"라고 명시되어 있습니다.'],
            
            ['P313', '영어', '고3', '객관식', '상', 
             'Artificial intelligence (AI) has made significant advances in recent years. Machine learning algorithms can now recognize patterns in data with remarkable accuracy. However, concerns about privacy and ethics remain. What is a concern mentioned in the passage regarding AI?', 
             'cost', 'privacy', 'size', 'speed', '', 
             'privacy', 'reading,comprehension,technology', '지문에서 "concerns about privacy and ethics remain"이라고 명시되어 있습니다.'],
            
            ['P314', '영어', '고2', '주관식', '상', 
             'The first airplane flight by the Wright brothers in 1903 lasted only 12 seconds and covered 120 feet. Today, commercial airplanes can fly non-stop for over 17 hours and cover more than 9,000 miles. How long did the Wright brothers\' first flight last?', 
             '', '', '', '', '', 
             '12 seconds', 'reading,comprehension,history', '지문에서 "The first airplane flight by the Wright brothers in 1903 lasted only 12 seconds"라고 명시되어 있습니다.'],
            
            ['P315', '영어', '고3', '주관식', '상', 
             'The average adult human body contains approximately 5 liters of blood. Blood is composed of red blood cells, white blood cells, platelets, and plasma. Plasma makes up about 55% of blood volume. What component makes up about 55% of blood volume?', 
             '', '', '', '', '', 
             'plasma', 'reading,comprehension,biology', '지문에서 "Plasma makes up about 55% of blood volume"이라고 명시되어 있습니다.']
        ]

        # 모든 샘플 문제 합치기
        all_sample_problems = (
            elementary_grammar_problems +
            elementary_vocabulary_problems +
            middle_grammar_problems +
            middle_vocabulary_problems +
            middle_reading_problems +
            high_grammar_problems +
            high_vocabulary_problems +
            high_reading_problems
        )
        
        # 문제 추가
        self.update_values('problems!A2:N46', all_sample_problems)
        logger.info(f"총 {len(all_sample_problems)}개의 샘플 문제가 추가되었습니다.")

    def ensure_sheets_exist(self):
        """스프레드시트에 필요한 시트(problems, student_answers)가 있는지 확인하고 없으면 생성합니다."""
        if not self.service:
            logger.error("Google Sheets API 서비스가 초기화되지 않았습니다.")
            return False
            
        try:
            # 현재 스프레드시트 정보 가져오기
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.SPREADSHEET_ID).execute()
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            
            # 필요한 시트 이름
            required_sheets = ['problems', 'student_answers']
            requests = []
            
            # 필요한 시트가 없으면 생성 요청 추가
            for sheet_name in required_sheets:
                if sheet_name not in existing_sheets:
                    logger.info(f"'{sheet_name}' 시트가 없습니다. 생성합니다.")
                    requests.append({
                        'addSheet': {
                            'properties': {
                                'title': sheet_name
                            }
                        }
                    })
            
            # 요청이 있으면 실행
            if requests:
                body = {'requests': requests}
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.SPREADSHEET_ID,
                    body=body
                ).execute()
                logger.info("필요한 시트를 생성했습니다.")
                
                # 시트 생성 후 헤더 설정
                self.initialize_sheets()
            else:
                logger.info("모든 필요한 시트가 이미 존재합니다.")
                
            return True
        except Exception as e:
            logger.error(f"시트 확인/생성 중 오류 발생: {str(e)}")
            return False
    
    def get_problems(self):
        """Get problems from the spreadsheet"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.SPREADSHEET_ID,
                range='problems!A2:N'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.info("문제 시트에 데이터가 없습니다.")
                return []
            
            # 열 이름
            columns = ['문제ID', '과목', '학년', '문제유형', '난이도', '문제내용', 
                '보기1', '보기2', '보기3', '보기4', '보기5', '정답', '키워드', '해설']
            
            # 데이터 형식 변환
            problems = []
            for row in values:
                # 행의 길이가 짧을 경우 빈 문자열로 채움
                row_data = row + [''] * (14 - len(row))
                
                # 딕셔너리로 변환
                problem = dict(zip(columns, row_data))
                problems.append(problem)
            
            logger.info(f"{len(problems)}개의 문제를 가져왔습니다.")
            return problems
        
        except Exception as e:
            logger.error(f"문제 가져오기 중 오류 발생: {str(e)}")
            return []

# 스프레드시트 데이터 가져오기 함수
def fetch_problems_from_sheet():
    """구글 시트에서 문제 데이터를 가져와 DataFrame으로 반환합니다."""
    try:
        sheets_setup = GoogleSheetsSetup()
        # 시트 존재 여부 확인 및 필요시 초기화
        sheets_setup.ensure_sheets_exist()
        
        # 문제 데이터 가져오기
        problems_data = sheets_setup.get_problems()
        if not problems_data:
            logger.warning("Google Sheets에서 가져온 문제 데이터가 없습니다.")
            return pd.DataFrame()
        
        # 데이터프레임으로 변환
        problems_df = pd.DataFrame(problems_data)
        return problems_df
    except Exception as e:
        logger.error(f"Google Sheets에서 문제를 가져오는 중 오류 발생: {str(e)}")
        return pd.DataFrame()

def main():
    """Main function to set up Google Sheets"""
    logger.info("Google Sheets 설정을 시작합니다...")
    
    sheets_setup = GoogleSheetsSetup()
    success = sheets_setup.initialize_sheets()
    
    if success:
        logger.info("Google Sheets 설정이 완료되었습니다.")
    else:
        logger.error("Google Sheets 설정 중 오류가 발생했습니다.")

if __name__ == "__main__":
    main() 