import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def main():
    try:
        print("테스트 시작")
        
        # 사용할 구글 API 범위
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        print("scope 설정 완료")
        
        # 서비스 계정 키 파일 경로
        credentials_path = 'credentials.json'
        
        # 자격 증명 생성
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        print("credentials 생성 완료")
        
        # 클라이언트 인증
        client = gspread.authorize(credentials)
        print("client 생성 완료")
        
        # 모든 스프레드시트 목록 가져오기
        try:
            print("\n사용 가능한 스프레드시트 목록:")
            spreadsheets = client.openall()
            if spreadsheets:
                for i, sheet in enumerate(spreadsheets):
                    print(f"{i+1}. {sheet.title} (ID: {sheet.id})")
            else:
                print("사용 가능한 스프레드시트가 없습니다.")
        except Exception as e:
            print(f"스프레드시트 목록 가져오기 오류: {str(e)}")
        
        # 여러 스프레드시트 ID 시도
        sheet_ids = [
            "1ke4Sv6TjOBua-hm-PLavMFHubA1mcJCrg0VVTJzf2d0",  # 원래 ID
            "1CuI3r03ZY3ljIIO310gKFMXp-pPZaZ4WFwfSbxrxqPw",  # 새 ID 1
            "1rVZ9cIMUPGLYTnzJ-07o3kfvpZHMBBaDnEnhW9G2cFc"   # 새 ID 2
        ]
        
        success = False
        for idx, sheet_id in enumerate(sheet_ids):
            try:
                print(f"\n시도 {idx+1}: 스프레드시트 ID {sheet_id} 열기 시도")
                spreadsheet = client.open_by_key(sheet_id)
                print(f"  - 스프레드시트 '{spreadsheet.title}' 열기 성공")
                
                # 첫 번째 시트 선택
                worksheet = spreadsheet.get_worksheet(0)
                print(f"  - 워크시트 '{worksheet.title}' 가져오기 완료")
                
                # 데이터 가져오기
                data = worksheet.get_all_records()
                print(f"  - 데이터 가져오기 성공: {len(data)}개의 레코드")
                
                # 데이터프레임으로 변환
                df = pd.DataFrame(data)
                print(f"  - 데이터프레임 변환 완료: {df.shape}")
                
                # 첫 5개 행 출력
                print("\n첫 5개 행:")
                print(df.head())
                
                success = True
                break
            except Exception as e:
                print(f"  - 오류 발생: {str(e)}")
        
        if not success:
            print("\n모든 스프레드시트 ID로 시도했지만 실패했습니다.")
            
            # 새 스프레드시트 생성 시도
            try:
                print("\n새 스프레드시트 생성 시도:")
                new_spreadsheet = client.create('테스트 스프레드시트')
                print(f"새 스프레드시트 생성 성공: {new_spreadsheet.title} (ID: {new_spreadsheet.id})")
                print(f"URL: https://docs.google.com/spreadsheets/d/{new_spreadsheet.id}/edit")
                
                # 테스트 데이터 추가
                worksheet = new_spreadsheet.sheet1
                worksheet.update_title("테스트 데이터")
                worksheet.update([
                    ["문제ID", "과목", "난이도", "문제내용"],
                    ["P001", "영어", "중", "테스트 문제 1"],
                    ["P002", "수학", "상", "테스트 문제 2"],
                    ["P003", "국어", "하", "테스트 문제 3"]
                ])
                print("테스트 데이터 추가 완료")
            except Exception as e:
                print(f"새 스프레드시트 생성 오류: {str(e)}")
                
        return success
    except Exception as e:
        print(f"전체 프로세스 오류: {str(e)}")
        return False

if __name__ == "__main__":
    main() 