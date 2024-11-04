# Google 서비스 관련 설정
from google.cloud import storage
from google.oauth2 import service_account
from googleapiclient.discovery import build

class GCSConfig:
    BUCKET_NAME = "teckwah-data"
    SERVICE_ACCOUNT_FILE = "/app/secrets/google/credentials.json"

    @staticmethod
    def get_client():
        return storage.Client.from_service_account_json(GCSConfig.SERVICE_ACCOUNT_FILE)


import pandas as pd
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class SheetsConfig:
    SHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'
    RANGE_NAME = 'Sheet1!A2:n637'
    SERVICE_ACCOUNT_FILE = "/app/secrets/google/credentials.json"
    COLUMNS = [
        'Delivery', 'Date', 'DPS', 'ETA', 'SLA', 'Address',
        'Status', 'Picked', 'Shipped', 'POD', 'Zip Code',
        'Billed Distance', 'Recipient', 'Issue'
    ]

    @staticmethod
    def get_service():
        credentials = service_account.Credentials.from_service_account_file(
            SheetsConfig.SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        return build('sheets', 'v4', credentials=credentials)

    @classmethod
    def fetch_sheet_data(cls):
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
