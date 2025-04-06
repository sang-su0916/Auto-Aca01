import os

class GoogleSheets:
    def __init__(self):
        """초기화 및 API 서비스 생성"""
        # 상수 정의
        self.credentials_file = 'credentials.json'
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        
        # 스프레드시트 ID
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0')
        
        # API 서비스 초기화
        self.service = self._create_service() 