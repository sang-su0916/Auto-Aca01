#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
구글 시트 ID 업데이트 스크립트
이 스크립트는 환경 변수 파일(.env)에 구글 시트 ID를 업데이트합니다.
"""

import os

# 구글 시트 ID
SPREADSHEET_ID = "1ke4Sv6TjOBua-hm-PLayMFHubA1mcJCrg0VVTJzf2d0"

def update_env_file():
    """환경 변수 파일(.env) 업데이트"""
    print("구글 시트 ID를 업데이트합니다...")
    print(f"사용할 스프레드시트 ID: {SPREADSHEET_ID}")
    
    # .env 파일이 존재하는지 확인
    if not os.path.exists('.env'):
        print(".env 파일이 존재하지 않습니다. 새로 생성합니다.")
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID}\n")
        print(".env 파일이 생성되었습니다.")
        return True
    
    # 기존 .env 파일 읽기
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # GOOGLE_SHEETS_SPREADSHEET_ID 환경 변수가 있는지 확인
        if 'GOOGLE_SHEETS_SPREADSHEET_ID=' in content:
            # 기존 ID 업데이트
            lines = content.split('\n')
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('GOOGLE_SHEETS_SPREADSHEET_ID='):
                    lines[i] = f'GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID}'
                    updated = True
                    break
            
            if not updated:
                # 환경 변수 이름은 있지만 라인으로 시작하지 않는 경우
                if not content.endswith('\n'):
                    content += '\n'
                content += f'GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID}\n'
                lines = content.split('\n')
            
            new_content = '\n'.join(lines)
        else:
            # 새 ID 추가
            if not content.endswith('\n'):
                content += '\n'
            new_content = content + f'GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID}\n'
        
        # 환경 변수 파일 업데이트
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f".env 파일에 구글 시트 ID가 업데이트되었습니다: {SPREADSHEET_ID}")
        return True
    
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        # 에러가 발생했을 경우 파일을 새로 작성
        try:
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(f"GOOGLE_SHEETS_SPREADSHEET_ID={SPREADSHEET_ID}\n")
            print(f".env 파일을 새로 생성했습니다. 구글 시트 ID: {SPREADSHEET_ID}")
            return True
        except Exception as e2:
            print(f"파일 생성 중 오류 발생: {str(e2)}")
            return False

if __name__ == "__main__":
    update_env_file()
    print("\n설정이 완료되었습니다.")
    print("이제 앱을 실행하면 지정된 구글 시트를 사용합니다.")
    print("\n구글 시트에 접근할 수 있는지 확인하려면:")
    print("1. 스프레드시트 설정에서 공유 > 이메일로 공유")
    print("2. credentials.json 파일에 있는 서비스 계정 이메일 추가")
    print("3. 편집자 권한 부여 후 완료\n") 