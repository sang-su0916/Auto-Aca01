from typing import List, Dict, Tuple
import re

class AutoGrader:
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
    
    def generate_feedback(self, score: int, found_keywords: List[str], all_keywords: List[str]) -> str:
        """Generate feedback based on grading results"""
        missing_keywords = [k for k in all_keywords if k not in found_keywords]
        
        feedback = []
        
        if score >= 90:
            feedback.append("훌륭한 답안입니다! 🌟")
        elif score >= 70:
            feedback.append("좋은 답안입니다. 👍")
        elif score >= 50:
            feedback.append("기본적인 내용은 포함되어 있습니다.")
        else:
            feedback.append("보완이 필요한 답안입니다.")
        
        if found_keywords:
            feedback.append(f"잘 설명된 부분: {', '.join(found_keywords)}")
        
        if missing_keywords:
            feedback.append(f"추가로 다루면 좋을 내용: {', '.join(missing_keywords)}")
        
        return "\n".join(feedback)
    
    def grade_answer(self, answer: str, model_answer: str, keywords: str) -> Tuple[int, str]:
        """Grade answer and generate feedback"""
        # Extract and preprocess keywords
        keyword_list = self.extract_keywords(keywords)
        
        # Calculate score
        score, found_keywords = self.calculate_keyword_score(answer, keyword_list)
        
        # Generate feedback
        feedback = self.generate_feedback(score, found_keywords, keyword_list)
        
        return score, feedback 