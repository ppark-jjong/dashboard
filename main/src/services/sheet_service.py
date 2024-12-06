from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from src.config import Config
import time

def fetch_google_sheets_data():
    """
    Google Sheets에서 데이터를 가져오는 함수
    """
    credentials = Credentials.from_service_account_file(
        Config.SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    # 데이터 가져오기
    result = sheet.values().get(spreadsheetId=Config.SPREADSHEET_ID, range=Config.RANGE_NAME).execute()
    rows = result.get("values", [])
    return rows

def run_periodic_fetch():
    """
    주기적으로 Google Sheets 데이터를 가져오는 함수
    """
    while True:
        print("Fetching data from Google Sheets...")
        data = fetch_google_sheets_data()
        print("Fetched Data:", data)
        time.sleep(Config.DATA_FETCH_INTERVAL)
