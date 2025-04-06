class FeedbackGenerator:
    """
    학생 답안에 대한 피드백을 생성하는 클래스
    다양한 피드백 생성 전략을 구현할 수 있습니다.
    """
    
    def __init__(self, feedback_templates=None):
        """
        FeedbackGenerator 초기화
        
        Args:
            feedback_templates (dict, optional): 피드백 템플릿 사전
        """
        # 기본 피드백 템플릿
        self.templates = {
            'excellent': [
                "아주 훌륭한 답안입니다!",
                "완벽한 이해도를 보여주는 답안입니다.",
                "정확한 개념 이해와 표현이 돋보입니다.",
                "핵심을 정확히 파악한 뛰어난 답안입니다."
            ],
            'good': [
                "좋은 답안입니다.",
                "대체로 정확한 이해를 보여줍니다.",
                "핵심 개념을 잘 파악했습니다.",
                "적절한 이해도를 보여주는 답안입니다."
            ],
            'fair': [
                "기본적인 내용은 이해하고 있습니다.",
                "일부 개념은 잘 파악했으나 보완이 필요합니다.",
                "핵심을 부분적으로 이해하고 있습니다.",
                "더 정확한 표현이 필요합니다."
            ],
            'poor': [
                "더 많은 학습이 필요합니다.",
                "핵심 개념에 대한 이해가 부족합니다.",
                "기본 내용을 다시 학습해보세요.",
                "주요 개념을 놓치고 있습니다."
            ],
            'keyword_found': [
                "다음 핵심 개념을 잘 이해했습니다: {found_keywords}",
                "다음 키워드를 효과적으로 활용했습니다: {found_keywords}",
                "{found_keywords} 개념을 정확히 사용했습니다.",
                "다음 요소를 잘 포함했습니다: {found_keywords}"
            ],
            'keyword_missing': [
                "다음 개념에 대해 더 학습하면 좋겠습니다: {missing_keywords}",
                "{missing_keywords} 개념이 답안에 누락되었습니다.",
                "다음 키워드를 추가로 학습해보세요: {missing_keywords}",
                "답안에 다음 핵심 요소가 빠져있습니다: {missing_keywords}"
            ],
            'length_short': [
                "답안이 모범 답안에 비해 너무 짧습니다. 더 자세히 설명해 보세요.",
                "더 상세한 설명이 필요합니다.",
                "내용을 더 풍부하게 보충해보세요.",
                "추가 설명이 필요합니다."
            ],
            'length_long': [
                "답안이 너무 길고 불필요한 내용이 많습니다. 핵심에 집중해 보세요.",
                "더 간결하게 핵심만 설명해보세요.",
                "불필요한 내용 없이 핵심에 집중하세요.",
                "답안이 주제에서 벗어난 내용을 포함하고 있습니다."
            ]
        }
        
        # 사용자 정의 템플릿으로 업데이트
        if feedback_templates:
            self.templates.update(feedback_templates)
    
    def generate_basic_feedback(self, score, found_keywords=None, missing_keywords=None, 
                               answer_length_issue=None):
        """
        기본 피드백 생성
        
        Args:
            score (int): 점수 (0-100)
            found_keywords (list, optional): 발견된 키워드 목록
            missing_keywords (list, optional): 누락된 키워드 목록
            answer_length_issue (str, optional): 답안 길이 문제 ('short', 'long', None)
            
        Returns:
            str: 생성된 피드백
        """
        import random
        feedback_parts = []
        
        # 점수별 기본 피드백
        if score >= 90:
            feedback_parts.append(random.choice(self.templates['excellent']))
        elif score >= 70:
            feedback_parts.append(random.choice(self.templates['good']))
        elif score >= 50:
            feedback_parts.append(random.choice(self.templates['fair']))
        else:
            feedback_parts.append(random.choice(self.templates['poor']))
        
        # 키워드 관련 피드백
        if found_keywords:
            template = random.choice(self.templates['keyword_found'])
            feedback_parts.append(template.format(found_keywords=', '.join(found_keywords)))
        
        if missing_keywords:
            template = random.choice(self.templates['keyword_missing'])
            feedback_parts.append(template.format(missing_keywords=', '.join(missing_keywords)))
        
        # 답안 길이 관련 피드백
        if answer_length_issue == 'short':
            feedback_parts.append(random.choice(self.templates['length_short']))
        elif answer_length_issue == 'long':
            feedback_parts.append(random.choice(self.templates['length_long']))
        
        return ' '.join(feedback_parts)
    
    def generate_detailed_feedback(self, score, answer, model_answer, 
                                  found_keywords=None, missing_keywords=None):
        """
        상세 피드백 생성 (기본 피드백 + 추가 분석)
        
        Args:
            score (int): 점수 (0-100)
            answer (str): 학생 답안
            model_answer (str): 모범 답안
            found_keywords (list, optional): 발견된 키워드 목록
            missing_keywords (list, optional): 누락된 키워드 목록
            
        Returns:
            str: 상세 피드백
        """
        # 답안 길이 분석
        answer_len = len(answer.strip())
        model_len = len(model_answer.strip())
        
        length_issue = None
        if answer_len < model_len * 0.5:
            length_issue = 'short'
        elif answer_len > model_len * 2:
            length_issue = 'long'
        
        # 기본 피드백 생성
        basic_feedback = self.generate_basic_feedback(
            score, found_keywords, missing_keywords, length_issue
        )
        
        # 추가 분석 및 피드백
        additional_feedback = self._analyze_answer_structure(answer, model_answer)
        
        if additional_feedback:
            return f"{basic_feedback} {additional_feedback}"
        return basic_feedback
    
    def _analyze_answer_structure(self, answer, model_answer):
        """
        답안의 구조 분석 (문장 수, 단락 구성 등)
        
        Args:
            answer (str): 학생 답안
            model_answer (str): 모범 답안
            
        Returns:
            str: 구조 분석 피드백
        """
        # 문장 수 비교
        answer_sentences = len([s for s in answer.split('.') if s.strip()])
        model_sentences = len([s for s in model_answer.split('.') if s.strip()])
        
        # 단락 수 비교
        answer_paragraphs = len([p for p in answer.split('\n\n') if p.strip()])
        model_paragraphs = len([p for p in model_answer.split('\n\n') if p.strip()])
        
        feedback = ""
        
        # 문장 구조 피드백
        if answer_sentences < model_sentences * 0.5:
            feedback += "답안의 문장 수가 적습니다. 더 다양한 문장으로 설명해보세요. "
        elif answer_sentences > model_sentences * 2:
            feedback += "문장이 너무 많습니다. 더 명확하고 간결한 문장으로 표현해보세요. "
        
        # 단락 구조 피드백
        if model_paragraphs > 1 and answer_paragraphs == 1:
            feedback += "내용을 여러 단락으로 구분하면 더 체계적인 답안이 됩니다. "
        
        return feedback.strip()


class AdvancedFeedbackGenerator(FeedbackGenerator):
    """
    개인화된 피드백과 학습 조언을 제공하는 고급 피드백 생성기
    """
    
    def __init__(self, feedback_templates=None, student_history=None):
        """
        고급 피드백 생성기 초기화
        
        Args:
            feedback_templates (dict, optional): 피드백 템플릿
            student_history (dict, optional): 학생별 이전 답안 및 점수 기록
        """
        super().__init__(feedback_templates)
        self.student_history = student_history or {}
    
    def generate_personalized_feedback(self, student_id, score, answer, model_answer,
                                      found_keywords, missing_keywords, problem_id=None):
        """
        학생 기록 기반 개인화된 피드백 생성
        
        Args:
            student_id (str): 학생 ID
            score (int): 점수
            answer (str): 학생 답안
            model_answer (str): 모범 답안
            found_keywords (list): 발견된 키워드
            missing_keywords (list): 누락된 키워드
            problem_id (str, optional): 문제 ID
            
        Returns:
            str: 개인화된 피드백
        """
        # 기본 피드백 생성
        basic_feedback = self.generate_detailed_feedback(
            score, answer, model_answer, found_keywords, missing_keywords
        )
        
        # 학생 기록이 없으면 기본 피드백 반환
        if not self.student_history or not student_id in self.student_history:
            return basic_feedback
        
        # 학생 기록 분석
        history = self.student_history[student_id]
        avg_score = self._calculate_average_score(history)
        
        # 성적 추세 분석
        trend_feedback = ""
        if score > avg_score + 10:
            trend_feedback = "이전 답안들보다 큰 향상을 보였습니다. 잘 하고 있습니다!"
        elif score < avg_score - 10:
            trend_feedback = "이전 답안들보다 점수가 낮습니다. 더 노력해보세요."
        
        # 반복적으로 놓치는 키워드 분석
        if 'missing_patterns' in history and missing_keywords:
            repeat_missing = set(history['missing_patterns']).intersection(missing_keywords)
            if repeat_missing:
                trend_feedback += f" {', '.join(repeat_missing)} 개념을 반복적으로 놓치고 있습니다. 특별히 학습해보세요."
        
        if trend_feedback:
            return f"{basic_feedback} {trend_feedback}"
        return basic_feedback
    
    def _calculate_average_score(self, history):
        """
        학생의 평균 점수 계산
        
        Args:
            history (dict): 학생 답안 기록
            
        Returns:
            float: 평균 점수
        """
        if 'scores' not in history or not history['scores']:
            return 0
            
        return sum(history['scores']) / len(history['scores'])
    
    def update_student_history(self, student_id, score, missing_keywords=None):
        """
        학생 기록 업데이트
        
        Args:
            student_id (str): 학생 ID
            score (int): 점수
            missing_keywords (list, optional): 누락된 키워드
        """
        if student_id not in self.student_history:
            self.student_history[student_id] = {'scores': [], 'missing_patterns': set()}
        
        self.student_history[student_id]['scores'].append(score)
        
        if missing_keywords:
            self.student_history[student_id]['missing_patterns'].update(missing_keywords)


# 모듈 사용 예시
if __name__ == "__main__":
    # 기본 피드백 생성기 테스트
    generator = FeedbackGenerator()
    
    feedback = generator.generate_basic_feedback(
        85, 
        found_keywords=["태양", "행성", "지구"],
        missing_keywords=["공전"],
        answer_length_issue="short"
    )
    print("기본 피드백:", feedback)
    
    # 상세 피드백 생성
    detailed = generator.generate_detailed_feedback(
        85,
        "태양계는 태양과 여러 행성으로 구성됩니다. 지구는 태양계의 행성입니다.",
        "태양계는 태양을 중심으로 8개의 행성이 공전하는 체계입니다. 지구는 태양으로부터 세 번째 행성이며, 생명체가 존재하는 유일한 행성으로 알려져 있습니다.",
        ["태양", "행성", "지구"],
        ["공전"]
    )
    print("\n상세 피드백:", detailed)
    
    # 개인화된 피드백 생성기 테스트
    advanced_generator = AdvancedFeedbackGenerator(
        student_history={
            "S12345": {
                "scores": [75, 80, 82],
                "missing_patterns": set(["공전", "중력"])
            }
        }
    )
    
    personalized = advanced_generator.generate_personalized_feedback(
        "S12345", 
        85,
        "태양계는 태양과 여러 행성으로 구성됩니다. 지구는 태양계의 행성입니다.",
        "태양계는 태양을 중심으로 8개의 행성이 공전하는 체계입니다. 지구는 태양으로부터 세 번째 행성이며, 생명체가 존재하는 유일한 행성으로 알려져 있습니다.",
        ["태양", "행성", "지구"],
        ["공전"]
    )
    print("\n개인화된 피드백:", personalized) 