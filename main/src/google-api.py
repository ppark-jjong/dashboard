# google_api.py

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Sheets API 설정
SHEET_ID = 'your_google_sheet_id'  # Google Sheets ID를 입력하세요.
RANGE_NAME = 'Sheet1!A2:E10'  # 데이터를 가져올 범위를 설정하세요.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'your_service_account_file.json'  # 서비스 계정 키 파일 경로

def get_sheet_data():
    """Google Sheets에서 데이터를 가져오는 함수"""
    try:
        # Google Sheets API 인증
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)

        # Google Sheets API 호출
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
        rows = result.get('values', [])
        return rows
    except HttpError as err:
        print(f"Google Sheets 데이터를 불러오는 중 오류 발생: {err}")
        return None
