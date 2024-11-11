import logging
import os
import pytz
import pandas as pd
from datetime import datetime
from google.cloud import storage
from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class GCSConfig:
    BUCKET_NAME = "teckwah-data"
    SERVICE_ACCOUNT_FILE = "/app/secrets/google/credentials.json"

    @staticmethod
    def get_client():
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/secrets/google/credentials.json")
        return storage.Client.from_service_account_json(credentials_path)


class TimestampConfig:
    TIMEZONE = "Asia/Seoul"

    @staticmethod
    def get_current_timestamp():
        """현재 로컬 시간대를 기준으로 타임스탬프를 반환"""
        return datetime.now(pytz.timezone(TimestampConfig.TIMEZONE))

    @staticmethod
    def format_timestamp(fmt="%y%m%d-%H%M"):
        """지정된 형식으로 타임스탬프를 반환"""
        return TimestampConfig.get_current_timestamp().strftime(fmt)


class SheetsConfig:
    SHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'
    RANGE_NAME = 'Sheet1!A2:n637'
    COLUMNS = [
        'Delivery', 'Date', 'DPS', 'ETA', 'SLA', 'Address',
        'Status', 'Picked', 'Shipped', 'POD', 'Zip Code',
        'Billed Distance', 'Recipient'
    ]

    @staticmethod
    def get_service():
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/secrets/google/credentials.json")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        return build('sheets', 'v4', credentials=credentials)

    @classmethod
    def fetch_sheet_data(cls):
        """Google Sheets에서 데이터를 가져와 DataFrame으로 반환"""
        try:
            service = cls.get_service()
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=cls.SHEET_ID, range=cls.RANGE_NAME).execute()
            rows = result.get('values', [])

            if not rows:
                logger.warning("Google Sheets에서 데이터를 찾을 수 없습니다.")
                return pd.DataFrame(columns=cls.COLUMNS)

            df = pd.DataFrame(rows[1:], columns=cls.COLUMNS)
            logger.info(f"{len(rows)}개의 데이터를 Google Sheets에서 가져왔습니다.")
            return df
        except Exception as e:
            logger.error(f"Google Sheets 데이터 가져오기 실패: {e}")
            return pd.DataFrame(columns=cls.COLUMNS)
