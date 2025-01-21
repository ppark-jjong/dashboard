from googleapiclient.discovery import build
from google.oauth2 import service_account

# 서비스 계정 키 파일 경로
SERVICE_ACCOUNT_FILE = "secrets/sheet-keys.json"

# Google Sheets ID 및 범위
SPREADSHEET_ID = "150yIrlRBBZNGMOJ-Rev6F80VmdTGFzS2FFsOEKTh5B4"  # Google Sheets ID
RANGE_NAME = "Delivery!A:I"  # 읽고 싶은 범위


def read_google_sheet():
    try:
        # 서비스 계정 인증
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )

        # Google Sheets API 클라이언트 생성
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()

        # 데이터 읽기 요청
        result = (
            sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        )
        rows = result.get("values", [])

        print(f"Retrieved {len(rows)} rows:")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    read_google_sheet()
