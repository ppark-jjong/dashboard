import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Sheets API 설정
SHEET_ID = os.environ.get('SHEET_ID', '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc')
RANGE_NAME = os.environ.get('RANGE_NAME', 'Sheet1!A1:o1000')
SERVICE_ACCOUNT_FILE = os.environ.get('SERVICE_ACCOUNT_FILE', 'C:/MyMain/oauth/google/credentials.json')

def get_sheet_data():
    try:
        # 설정된 값들을 출력하여 확인
        print(f"SHEET_ID: {SHEET_ID}")
        print(f"RANGE_NAME: {RANGE_NAME}")
        print(f"SERVICE_ACCOUNT_FILE: {SERVICE_ACCOUNT_FILE}")

        # SERVICE_ACCOUNT_FILE 경로 확인
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"Service account file이 존재하지 않습니다: {SERVICE_ACCOUNT_FILE}")
            return None

        # Google Sheets API 인증
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        service = build('sheets', 'v4', credentials=credentials)

        # Google Sheets API 호출
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
        rows = result.get('values', [])
        print(f"Fetched rows: {rows}")  # 데이터 가져온 후 출력
        return rows
    except HttpError as err:
        print(f"Google Sheets 데이터를 불러오는 중 오류 발생: {err}")
        return None
    except Exception as e:
        print(f"예기치 않은 오류 발생: {e}")
        return None

