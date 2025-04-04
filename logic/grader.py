from typing import List, Dict, Tuple, Any, Optional
import re

class Grader:
    """자동 채점 시스템 클래스"""
    
    def __init__(self):
        self.max_score = 100
        self.min_score = 0
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for comparison"""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Split by comma and clean
        if ',' in text:
            keywords = [k.strip() for k in text.split(',')]
        else:
            keywords = [text.strip()]
        return [self.preprocess_text(k) for k in keywords if k]
    
    def calculate_keyword_score(self, answer: str, keywords: List[str]) -> Tuple[int, List[str]]:
        """Calculate score based on keywords presence"""
        preprocessed_answer = self.preprocess_text(answer)
        found_keywords = []
        
        for keyword in keywords:
            if keyword in preprocessed_answer:
                found_keywords.append(keyword)
        
        if not keywords:
            return 0, []
        
        # Calculate score based on keyword matches
        score = int((len(found_keywords) / len(keywords)) * self.max_score)
        return score, found_keywords
    
    def generate_feedback(self, score: int, answer_analysis: Dict[str, Any], 
                         problem_type: str) -> str:
        """
        채점 결과에 따른 상세 피드백 생성
        
        Args:
            score (int): 채점 점수
            answer_analysis (Dict[str, Any]): 답안 분석 결과
            problem_type (str): 문제 유형 ('객관식', '주관식', '서술형')
            
        Returns:
            str: 상세 피드백
        """
        if problem_type == '객관식':
            if score == 100:
                return "정답입니다!"
            else:
                return "오답입니다. 다시 한번 선택지를 검토해보세요."
        
        elif problem_type == '주관식':
            if score == 100:
                return "정답입니다! 완벽한 답변이네요."
            elif score >= 80:
                missing = [k for k in answer_analysis.get("total_keywords", []) 
                          if k not in answer_analysis.get("keyword_matches", [])]
                if missing:
                    return f"거의 정답입니다! 추가로 고려해볼 키워드: {', '.join(missing[:2])}"
                else:
                    return "거의 정답입니다! 표현 방식에 약간의 차이가 있습니다."
            elif score >= 50:
                return f"부분 정답입니다. 핵심 개념을 잘 파악했지만, 좀 더 정확한 표현이 필요합니다."
            else:
                return "더 정확한 답변이 필요합니다. 핵심 개념을 다시 학습해보세요."
        
        elif problem_type == '서술형':
            if score >= 80:
                return "우수한 답변입니다! 핵심 개념을 잘 이해하고 있습니다."
            elif score >= 60:
                return "좋은 답변입니다. 몇 가지 중요한 포인트를 잘 설명했습니다."
            elif score >= 40:
                return "보통 수준의 답변입니다. 더 많은 핵심 개념을 포함시켜보세요."
            else:
                return "기초적인 답변입니다. 더 자세한 설명과 예시가 필요합니다."
        
        return "답변을 검토했습니다. 교사의 추가 확인이 필요할 수 있습니다."
    
    def grade_answer(self, problem_type: str, correct_answer: str, 
                     user_answer: str, keywords: Optional[str] = None) -> Tuple[int, str]:
        """
        학생 답안 채점 기능
        
        Args:
            problem_type (str): 문제 유형 ('객관식', '주관식', '서술형')
            correct_answer (str): 정답 또는 모범답안
            user_answer (str): 학생 제출 답안
            keywords (Optional[str]): 핵심 키워드 (쉼표로 구분)
            
        Returns:
            Tuple[int, str]: (점수, 피드백)
        """
        if not user_answer:
            return 0, "답변을 입력하지 않았습니다."
        
        # 객관식 문제 채점
        if problem_type == '객관식':
            return self._grade_multiple_choice(correct_answer, user_answer)
        
        # 주관식 문제 채점
        elif problem_type == '주관식':
            return self._grade_short_answer(correct_answer, user_answer, keywords)
        
        # 서술형 문제 채점
        elif problem_type == '서술형':
            return self._grade_essay(correct_answer, user_answer, keywords)
        
        return 0, "알 수 없는 문제 유형입니다."
    
    def _grade_multiple_choice(self, correct_answer: str, user_answer: str) -> Tuple[int, str]:
        """객관식 문제 채점"""
        if user_answer.strip().lower() == correct_answer.strip().lower():
            return 100, "정답입니다!"
        else:
            return 0, f"오답입니다. 정답은 '{correct_answer}'입니다."
    
    def _grade_short_answer(self, correct_answer: str, user_answer: str, 
                          keywords: Optional[str] = None) -> Tuple[int, str]:
        """주관식 문제 채점"""
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        
        # 정확히 일치하는 경우
        if user_answer == correct_answer:
            return 100, "정답입니다!"
        
        # 키워드 기반 부분 점수 채점
        if keywords:
            keyword_list = [k.strip().lower() for k in keywords.split(',')]
            matched_keywords = [k for k in keyword_list if k in user_answer]
            
            if matched_keywords:
                score = min(100, int(len(matched_keywords) / len(keyword_list) * 100))
                if score >= 80:
                    feedback = f"거의 정답입니다! 포함된 키워드: {', '.join(matched_keywords)}"
                elif score >= 50:
                    feedback = f"부분 정답입니다. 포함된 키워드: {', '.join(matched_keywords)}"
                else:
                    feedback = f"더 정확한 답변이 필요합니다. 정답은 '{correct_answer}'입니다."
                return score, feedback
        
        # 기본 피드백
        return 0, f"오답입니다. 정답은 '{correct_answer}'입니다."
    
    def _grade_essay(self, correct_answer: str, user_answer: str, 
                   keywords: Optional[str] = None) -> Tuple[int, str]:
        """서술형 문제 채점"""
        user_answer = user_answer.strip().lower()
        
        # 키워드 기반 채점
        if keywords:
            keyword_list = [k.strip().lower() for k in keywords.split(',')]
            matched_keywords = [k for k in keyword_list if k in user_answer]
            
            score = min(100, int(len(matched_keywords) / len(keyword_list) * 100))
            
            if score >= 80:
                feedback = f"우수한 답변입니다! 포함된 키워드: {', '.join(matched_keywords)}"
            elif score >= 60:
                feedback = f"좋은 답변입니다. 포함된 키워드: {', '.join(matched_keywords)}"
            elif score >= 40:
                feedback = f"보통 수준의 답변입니다. 추가 키워드: {', '.join([k for k in keyword_list if k not in matched_keywords])}"
            else:
                feedback = f"더 자세한 답변이 필요합니다. 주요 키워드: {', '.join(keyword_list)}"
            
            return score, feedback
        
        # 기본 피드백
        return 50, "키워드 정보가 없어 정확한 채점이 어렵습니다. 교사의 확인이 필요합니다."
    
    def analyze_answer(self, user_answer: str, correct_answer: str, 
                      keywords: Optional[str] = None) -> Dict[str, Any]:
        """
        학생 답안 상세 분석
        
        Args:
            user_answer (str): 학생 제출 답안
            correct_answer (str): 정답 또는 모범답안
            keywords (Optional[str]): 핵심 키워드 (쉼표로 구분)
            
        Returns:
            Dict[str, Any]: 답안 분석 결과
        """
        result = {
            "length_ratio": min(1.0, len(user_answer) / len(correct_answer) if len(correct_answer) > 0 else 0),
            "exact_match": user_answer.strip().lower() == correct_answer.strip().lower(),
            "keyword_matches": [],
            "keyword_count": 0,
            "total_keywords": 0
        }
        
        if keywords:
            keyword_list = [k.strip().lower() for k in keywords.split(',')]
            matched_keywords = [k for k in keyword_list if k in user_answer.lower()]
            
            result["keyword_matches"] = matched_keywords
            result["keyword_count"] = len(matched_keywords)
            result["total_keywords"] = len(keyword_list)
            result["keyword_ratio"] = len(matched_keywords) / len(keyword_list) if len(keyword_list) > 0 else 0
        
        return result 