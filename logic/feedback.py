from typing import Dict, List, Any, Optional
import re

class FeedbackGenerator:
    """자동 첨삭 및 피드백 생성 시스템"""
    
    def __init__(self):
        # 영어 문법 및 표현 관련 패턴 정의
        self.grammar_patterns = {
            r"\b(is|am|are|was|were)\s+\w+ing\b": "진행형 시제 사용",
            r"\b(have|has|had)\s+\w+ed\b|\b(have|has|had)\s+\w+ten\b|\b(have|has|had)\s+\w+ne\b": "완료형 시제 사용",
            r"\bwill\s+\w+\b": "미래 시제 사용",
            r"\b(a|an|the)\s+\w+\b": "관사 사용",
            r"\b\w+s\b": "복수형 또는 3인칭 단수 사용",
            r"\b(if|when|although|because|since|while)\s+.+\b": "종속절 사용"
        }
        
        # 영어 문법 오류 패턴
        self.error_patterns = {
            r"\b(is|am|are|was|were)\s+\w+ed\b|\b(is|am|are|was|were)\s+\w+ten\b|\b(is|am|are|was|were)\s+\w+ne\b": 
                "시제 오류: 'be 동사 + 과거분사'는 수동태 형태입니다. 현재 진행형을 의도했다면 '-ing' 형태를 사용하세요.",
            
            r"\b(have|has|had)\s+\w+ing\b": 
                "시제 오류: 현재완료는 'have/has + 과거분사' 형태를 사용해야 합니다.",
            
            r"\b(I|we|you|they)\s+is\b|\b(he|she|it)\s+are\b|\b(he|she|it)\s+am\b|\b(you|we|they)\s+am\b|\bI\s+are\b": 
                "주어-동사 일치 오류: 주어와 be동사가 일치하지 않습니다.",
            
            r"\ba\s+[aeiou]\w+\b": 
                "관사 오류: 모음으로 시작하는 단어 앞에는 'an'을 사용해야 합니다.",
            
            r"\ban\s+[^aeiou\s]\w+\b": 
                "관사 오류: 자음으로 시작하는 단어 앞에는 'a'를 사용해야 합니다."
        }
    
    def analyze_english_answer(self, answer: str) -> Dict[str, Any]:
        """
        영어 답안 분석
        
        Args:
            answer (str): 학생 답안
            
        Returns:
            Dict[str, Any]: 답안 분석 결과
        """
        if not answer or not isinstance(answer, str):
            return {"error": "유효하지 않은 답안입니다."}
        
        words = answer.split()
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        analysis = {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_words_per_sentence": len(words) / len(sentences) if sentences else 0,
            "grammar_patterns": [],
            "grammar_errors": [],
            "vocabulary_level": self._assess_vocabulary_level(words)
        }
        
        # 문법 패턴 확인
        for pattern, description in self.grammar_patterns.items():
            matches = re.findall(pattern, answer, re.IGNORECASE)
            if matches:
                analysis["grammar_patterns"].append({
                    "description": description,
                    "examples": matches[:3]  # 최대 3개 예시만 포함
                })
        
        # 문법 오류 확인
        for pattern, description in self.error_patterns.items():
            matches = re.findall(pattern, answer, re.IGNORECASE)
            if matches:
                analysis["grammar_errors"].append({
                    "description": description,
                    "examples": matches[:3]  # 최대 3개 예시만 포함
                })
        
        return analysis
    
    def _assess_vocabulary_level(self, words: List[str]) -> str:
        """
        어휘 수준 평가 (간단한 휴리스틱 사용)
        
        Args:
            words (List[str]): 단어 목록
            
        Returns:
            str: 어휘 수준 (기초, 중급, 고급)
        """
        # 더 정교한 방법을 위해서는 외부 어휘 데이터베이스 또는 API 사용 필요
        advanced_words = ["subsequently", "nevertheless", "furthermore", "consequently", "precisely",
                         "determine", "establish", "facilitate", "implement", "integrate",
                         "paradigm", "hierarchy", "subsequent", "preliminary", "fundamental"]
        
        intermediate_words = ["however", "therefore", "although", "several", "various",
                            "consider", "provide", "suggest", "require", "contain",
                            "specific", "particular", "additional", "significant", "effective"]
        
        # 고급 단어 비율
        advanced_count = sum(1 for word in words if word.lower() in advanced_words)
        intermediate_count = sum(1 for word in words if word.lower() in intermediate_words)
        
        advanced_ratio = advanced_count / len(words) if words else 0
        intermediate_ratio = intermediate_count / len(words) if words else 0
        
        if advanced_ratio > 0.1:  # 10% 이상이 고급 단어
            return "고급"
        elif intermediate_ratio > 0.15 or (intermediate_ratio > 0.1 and advanced_ratio > 0.05):
            return "중급"
        else:
            return "기초"
    
    def generate_detailed_feedback(self, answer: str, analysis: Dict[str, Any], 
                                  score: int, problem_type: str) -> str:
        """
        상세 첨삭 및 피드백 생성
        
        Args:
            answer (str): 학생 답안
            analysis (Dict[str, Any]): 답안 분석 결과
            score (int): 점수
            problem_type (str): 문제 유형
            
        Returns:
            str: 상세 피드백
        """
        feedback = []
        
        # 점수별 기본 피드백
        if score >= 90:
            feedback.append("우수한 답변입니다! 👏")
        elif score >= 70:
            feedback.append("좋은 답변입니다.")
        elif score >= 50:
            feedback.append("괜찮은 답변이지만 개선의 여지가 있습니다.")
        else:
            feedback.append("더 많은 연습이 필요합니다.")
        
        # 문제 유형별 피드백
        if problem_type == '주관식' or problem_type == '서술형':
            # 문장 구조에 대한 피드백
            if analysis.get("sentence_count", 0) > 0:
                avg_words = analysis.get("avg_words_per_sentence", 0)
                if avg_words < 5:
                    feedback.append("문장이 너무 짧습니다. 더 자세한 표현을 사용해보세요.")
                elif avg_words > 20:
                    feedback.append("문장이 너무 깁니다. 간결하게 표현하는 연습을 해보세요.")
            
            # 어휘 수준에 대한 피드백
            vocab_level = analysis.get("vocabulary_level", "")
            if vocab_level == "고급":
                feedback.append("다양한 고급 어휘를 효과적으로 사용했습니다.")
            elif vocab_level == "중급":
                feedback.append("적절한 어휘를 사용했습니다. 더 다양한 표현에 도전해보세요.")
            else:
                feedback.append("기초적인 어휘를 사용했습니다. 더 다양한 어휘를 학습해보세요.")
            
            # 문법 패턴 사용에 대한 피드백
            patterns = analysis.get("grammar_patterns", [])
            if patterns:
                pattern_desc = [p["description"] for p in patterns]
                feedback.append(f"다양한 문법 구조를 사용했습니다: {', '.join(pattern_desc[:3])}.")
            else:
                feedback.append("더 다양한 문법 구조를 활용해보세요.")
            
            # 문법 오류에 대한 피드백
            errors = analysis.get("grammar_errors", [])
            if errors:
                feedback.append("다음과 같은 문법적 개선이 필요합니다:")
                for err in errors[:3]:  # 최대 3개까지만 표시
                    feedback.append(f"- {err['description']}")
        
        # 최종 피드백 생성
        return "\n".join(feedback)
    
    def generate_improvement_suggestions(self, answer: str, score: int, 
                                        correct_answer: Optional[str] = None) -> List[str]:
        """
        답안 개선 제안
        
        Args:
            answer (str): 학생 답안
            score (int): 점수
            correct_answer (Optional[str]): 모범 답안
            
        Returns:
            List[str]: 개선 제안 목록
        """
        suggestions = []
        
        # 점수별 개선 제안
        if score < 40:
            suggestions.append("기본 문법 규칙을 다시 학습해보세요.")
            suggestions.append("간단한 문장부터 연습해보세요.")
        elif score < 70:
            suggestions.append("더 다양한 어휘를 사용해보세요.")
            suggestions.append("복합 문장 구조를 연습해보세요.")
        else:
            suggestions.append("더 자연스러운 표현을 위해 영어 글쓰기 연습을 계속하세요.")
            suggestions.append("다양한 주제에 대해 글을 써보세요.")
        
        # 모범 답안이 있는 경우, 추가 제안
        if correct_answer:
            # 문장 길이 비교
            correct_sentences = re.split(r'[.!?]+', correct_answer)
            correct_sentences = [s.strip() for s in correct_sentences if s.strip()]
            
            answer_sentences = re.split(r'[.!?]+', answer)
            answer_sentences = [s.strip() for s in answer_sentences if s.strip()]
            
            if len(answer_sentences) < len(correct_sentences):
                suggestions.append("답변이 너무 짧습니다. 더 자세한 설명을 추가해보세요.")
            
            # 특정 키워드 사용 여부 확인
            correct_words = correct_answer.lower().split()
            answer_words = answer.lower().split()
            
            missing_keywords = [word for word in correct_words if len(word) > 4 and word not in answer_words]
            if missing_keywords:
                suggestions.append(f"다음 키워드를 포함해보세요: {', '.join(missing_keywords[:3])}")
        
        return suggestions 