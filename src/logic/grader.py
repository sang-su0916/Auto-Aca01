class Grader:
    """
    학생 답안 채점을 위한 기본 클래스
    키워드 기반 채점 알고리즘을 구현합니다.
    """
    
    def __init__(self, max_score=100):
        """
        Grader 클래스 초기화
        
        Args:
            max_score (int): 만점 점수
        """
        self.max_score = max_score
    
    def grade_answer(self, answer, model_answer, keywords, difficulty="중"):
        """
        키워드 기반으로 학생 답안 채점
        
        Args:
            answer (str): 학생 답안
            model_answer (str): 모범 답안
            keywords (list): 채점 키워드 목록
            difficulty (str): 문제 난이도 (상/중/하)
            
        Returns:
            tuple: (점수, 피드백)
        """
        if not answer or not keywords:
            return 0, "답안이 제출되지 않았거나 채점 키워드가 없습니다."
        
        # 답안과 키워드를 소문자로 변환하여 비교
        answer_lower = answer.lower()
        
        # 키워드를 문자열로 받았을 경우 리스트로 변환
        if isinstance(keywords, str):
            keywords = keywords.split(',')
        
        # 답안에 포함된 키워드 수 계산
        found_keywords = []
        missing_keywords = []
        
        for keyword in keywords:
            keyword = keyword.strip().lower()
            if keyword in answer_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # 키워드 포함 비율에 따른 점수 계산
        if not keywords:
            return 0, "채점 키워드가 정의되지 않았습니다."
            
        keyword_ratio = len(found_keywords) / len(keywords)
        
        # 난이도별 가중치 (상: 0.8, 중: 1.0, 하: 1.2)
        difficulty_weight = {
            "상": 0.8,  # 어려운 문제는 같은 키워드 포함 비율에도 가중치 적용
            "중": 1.0,
            "하": 1.2   # 쉬운 문제는 키워드가 많이 포함되어야 높은 점수
        }
        
        weight = difficulty_weight.get(difficulty, 1.0)
        
        # 최종 점수 계산 (난이도 가중치 적용)
        score = int(self.max_score * keyword_ratio * weight)
        
        # 점수 상한/하한 적용
        score = max(0, min(self.max_score, score))
        
        # 피드백 생성
        feedback = self._generate_feedback(
            answer, model_answer, found_keywords, missing_keywords, score
        )
        
        return score, feedback
    
    def _generate_feedback(self, answer, model_answer, found_keywords, missing_keywords, score):
        """
        점수와 키워드 포함 여부에 따른 피드백 생성
        
        Args:
            answer (str): 학생 답안
            model_answer (str): 모범 답안
            found_keywords (list): 답안에 포함된 키워드
            missing_keywords (list): 답안에 누락된 키워드
            score (int): 계산된 점수
            
        Returns:
            str: 채점 결과에 대한 피드백
        """
        feedback = ""
        
        # 점수별 피드백
        if score >= 90:
            feedback += "아주 훌륭한 답안입니다! "
        elif score >= 70:
            feedback += "좋은 답안입니다. "
        elif score >= 50:
            feedback += "기본적인 내용은 이해하고 있습니다. "
        else:
            feedback += "더 많은 학습이 필요합니다. "
        
        # 키워드 포함 관련 피드백
        if found_keywords:
            feedback += f"다음 핵심 개념을 잘 이해했습니다: {', '.join(found_keywords)}. "
        
        # 누락된 키워드 관련 피드백
        if missing_keywords:
            feedback += f"다음 개념에 대해 더 학습하면 좋겠습니다: {', '.join(missing_keywords)}. "
        
        # 모범 답안과의 비교 피드백
        answer_len = len(answer.strip())
        model_len = len(model_answer.strip())
        
        if answer_len < model_len * 0.5:
            feedback += "답안이 모범 답안에 비해 너무 짧습니다. 더 자세히 설명해 보세요. "
        elif answer_len > model_len * 2:
            feedback += "답안이 너무 길고 불필요한 내용이 많습니다. 핵심에 집중해 보세요. "
        
        return feedback.strip()


class AutoGrader(Grader):
    """
    자동 채점 시스템
    기본 Grader를 확장하여 더 복잡한 채점 로직 구현 가능
    """
    
    def __init__(self, max_score=100, keyword_weight=0.7, content_weight=0.3):
        """
        AutoGrader 초기화
        
        Args:
            max_score (int): 만점
            keyword_weight (float): 키워드 기반 점수 가중치
            content_weight (float): 내용 분석 점수 가중치
        """
        super().__init__(max_score)
        self.keyword_weight = keyword_weight
        self.content_weight = content_weight
    
    def grade_answer(self, answer, model_answer, keywords, difficulty="중"):
        """
        키워드 기반 + 내용 분석 복합 채점
        
        Args:
            answer (str): 학생 답안
            model_answer (str): 모범 답안
            keywords (list): 채점 키워드 목록
            difficulty (str): 문제 난이도
            
        Returns:
            tuple: (점수, 피드백)
        """
        # 기본 키워드 채점
        keyword_score, keyword_feedback = super().grade_answer(
            answer, model_answer, keywords, difficulty
        )
        
        # 내용 유사성 점수 계산 (간단한 버전)
        # 실제 구현에서는 더 정교한 알고리즘 적용 가능
        content_score = self._analyze_content_similarity(answer, model_answer)
        
        # 가중 평균 최종 점수 계산
        final_score = int(
            keyword_score * self.keyword_weight + 
            content_score * self.content_weight
        )
        
        # 점수 상한/하한 적용
        final_score = max(0, min(self.max_score, final_score))
        
        # 최종 피드백 생성
        final_feedback = self._generate_advanced_feedback(
            answer, model_answer, keywords, 
            keyword_score, content_score, final_score
        )
        
        return final_score, final_feedback
    
    def _analyze_content_similarity(self, answer, model_answer):
        """
        답안과 모범답안의 내용 유사성 분석 (기본 구현)
        
        Args:
            answer (str): 학생 답안
            model_answer (str): 모범 답안
            
        Returns:
            int: 내용 유사성 점수 (0-100)
        """
        # 간단한 내용 유사성 비교 (단어 기반)
        answer_words = set(answer.lower().split())
        model_words = set(model_answer.lower().split())
        
        # 공통 단어 비율 계산
        if not model_words:
            return 0
            
        common_words = answer_words.intersection(model_words)
        similarity_ratio = len(common_words) / len(model_words)
        
        return int(self.max_score * similarity_ratio)
    
    def _generate_advanced_feedback(self, answer, model_answer, keywords, 
                                   keyword_score, content_score, final_score):
        """
        향상된 피드백 생성
        
        Args:
            answer (str): 학생 답안
            model_answer (str): 모범 답안
            keywords (list): 키워드 목록
            keyword_score (int): 키워드 기반 점수
            content_score (int): 내용 유사성 점수
            final_score (int): 최종 점수
            
        Returns:
            str: 상세 피드백
        """
        # 기본 피드백 생성
        basic_feedback = self._generate_feedback(
            answer, model_answer, [], [], final_score
        )
        
        # 내용 유사성 관련 피드백 추가
        similarity_feedback = ""
        if content_score < 50:
            similarity_feedback = "모범 답안과 다른 접근 방식을 사용했습니다. "
            if final_score > 70:
                similarity_feedback += "그러나 핵심 개념은 잘 이해하고 있습니다."
            else:
                similarity_feedback += "핵심 내용을 더 정확히 이해할 필요가 있습니다."
        
        # 점수 분석 피드백 추가
        score_analysis = f"키워드 활용도: {keyword_score}점, 내용 유사성: {content_score}점"
        
        return f"{basic_feedback} {similarity_feedback} ({score_analysis})"


# 모듈 사용 예시
if __name__ == "__main__":
    # 기본 채점기 테스트
    grader = Grader()
    answer = "태양계는 태양과 8개의 행성으로 구성되어 있으며, 지구는 태양으로부터 3번째 행성입니다."
    model_answer = "태양계는 태양을 중심으로 8개의 행성이 공전하는 체계이며, 지구는 3번째 행성입니다."
    keywords = ["태양", "행성", "지구", "공전"]
    
    score, feedback = grader.grade_answer(answer, model_answer, keywords)
    print(f"점수: {score}")
    print(f"피드백: {feedback}")
    
    # 고급 채점기 테스트
    auto_grader = AutoGrader()
    auto_score, auto_feedback = auto_grader.grade_answer(answer, model_answer, keywords)
    print(f"\n자동 채점 점수: {auto_score}")
    print(f"자동 채점 피드백: {auto_feedback}") 