from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# 서비스 계정 자격 증명 파일 경로
SERVICE_ACCOUNT_FILE = 'C:\MyMain\oauth\google\credentials.json'

# Google Sheets API와 연결할 범위 설정
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# 자격 증명 설정
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Google Sheets API 서비스 생성
service = build('sheets', 'v4', credentials=creds)

# Google Sheets ID와 범위 설정
SPREADSHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'  # 사용할 구글 시트의 ID를 입력
RANGE_NAME = 'sheet1!A1:O1000'  # 읽고자 하는 시트와 범위 설정

# 데이터 가져오기
try:
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Data from Google Sheets:')
        for row in values:
            print(row)

except Exception as e:
    print(f"Error occurred: {e}")
