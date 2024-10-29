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


class SheetsConfig:
    SHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'
    RANGE_NAME = 'Sheet1!A2:n637'
    SERVICE_ACCOUNT_FILE = "/app/secrets/google/credentials.json"

    @staticmethod
    def get_service():
        credentials = service_account.Credentials.from_service_account_file(
            SheetsConfig.SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        return build('sheets', 'v4', credentials=credentials)
