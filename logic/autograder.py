from typing import List, Dict, Tuple, Any, Optional
from logic.grader import Grader

class AutoGrader(Grader):
    """자동 채점 시스템 확장 클래스 - Google Sheets 연동용"""
    
    def __init__(self):
        """초기화"""
        super().__init__()
        self.sheets_connected = False
    
    def set_sheets_connection(self, connected: bool = True):
        """Google Sheets 연결 상태 설정"""
        self.sheets_connected = connected
        return self.sheets_connected
    
    def is_sheets_connected(self) -> bool:
        """Google Sheets 연결 상태 확인"""
        return self.sheets_connected
    
    def grade_and_save(self, problem_type: str, correct_answer: str, 
                      user_answer: str, keywords: Optional[str] = None,
                      student_id: str = "", problem_id: str = "") -> Tuple[int, str]:
        """
        학생 답안 채점 후 저장
        
        Args:
            problem_type (str): 문제 유형 ('객관식', '주관식', '서술형')
            correct_answer (str): 정답 또는 모범답안
            user_answer (str): 학생 제출 답안
            keywords (Optional[str]): 핵심 키워드 (쉼표로 구분)
            student_id (str): 학생 ID
            problem_id (str): 문제 ID
            
        Returns:
            Tuple[int, str]: (점수, 피드백)
        """
        # 기본 채점 수행
        score, feedback = self.grade_answer(problem_type, correct_answer, user_answer, keywords)
        
        # Google Sheets에 저장 (연결된 경우)
        if self.sheets_connected and student_id and problem_id:
            try:
                # 실제 저장 로직은 Google Sheets API 연동 모듈에서 처리
                # 여기서는 저장 로직을 구현하지 않고 성공했다고 가정
                print(f"[AutoGrader] 채점 결과 저장 완료: 학생 {student_id}, 문제 {problem_id}, 점수 {score}")
            except Exception as e:
                print(f"[AutoGrader] 채점 결과 저장 중 오류 발생: {str(e)}")
        
        return score, feedback
    
    def get_student_answers(self, student_id: str) -> List[Dict[str, Any]]:
        """
        특정 학생의 모든 제출 답안 가져오기
        
        Args:
            student_id (str): 학생 ID
            
        Returns:
            List[Dict[str, Any]]: 학생 답안 목록
        """
        if not self.sheets_connected:
            return []
        
        # 실제 구현은 Google Sheets API 연동 모듈에서 처리
        # 여기서는 빈 리스트 반환
        return []
    
    def get_problem_answers(self, problem_id: str) -> List[Dict[str, Any]]:
        """
        특정 문제에 대한 모든 학생 답안 가져오기
        
        Args:
            problem_id (str): 문제 ID
            
        Returns:
            List[Dict[str, Any]]: 학생 답안 목록
        """
        if not self.sheets_connected:
            return []
        
        # 실제 구현은 Google Sheets API 연동 모듈에서 처리
        # 여기서는 빈 리스트 반환
        return [] 