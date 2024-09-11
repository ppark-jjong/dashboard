from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from kafka import KafkaProducer
import json

# Google Sheets API 설정
SERVICE_ACCOUNT_FILE = 'C:\MyMain\oauth\google\credentials.json'  # 서비스 계정 키 파일 경로
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'  # 스프레드시트 ID
RANGE_NAME = 'Sheet1!A1:D10'  # 읽을 범위

# Kafka 설정
KAFKA_BROKER = 'localhost:9092'  # Kafka 브로커 주소
TOPIC_NAME = 'sheets-data'  # 전송할 Kafka 토픽 이름

# Google Sheets API 인증 설정
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)


# Google Sheets 데이터 가져오기
def fetch_sheet_data():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    return values


# Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers=['localhost:29092'],  # 'localhost:29092' 대신 'kafka:9092' 사용
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)


# Google Sheets 데이터를 Kafka로 전송
def send_data_to_kafka(data):
    for row in data:
        # 각 row 데이터를 JSON 형식으로 Kafka로 전송
        producer.send(TOPIC_NAME, value=row)
        print(f"Sent to Kafka: {row}")


# 메인 로직 실행
if __name__ == '__main__':
    sheet_data = fetch_sheet_data()  # Google Sheets에서 데이터 가져오기
    if sheet_data:
        print('Fetched data from Google Sheets:')
        for row in sheet_data:
            print(row)
        send_data_to_kafka(sheet_data)  # Kafka로 데이터 전송
    else:
        print('No data found in Google Sheets.')

# Producer 종료
producer.flush()
producer.close()
