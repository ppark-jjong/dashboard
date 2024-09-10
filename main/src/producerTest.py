from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from kafka import KafkaProducer
import json

# Google Sheets API 설정
SERVICE_ACCOUNT_FILE = 'C:\MyMain\oauth\google\credentials.json'  # 서비스 계정 자격 증명 파일 경로
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Google Sheets ID와 범위 설정
SPREADSHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'  # 사용할 구글 시트의 ID를 입력
RANGE_NAME = 'sheet1!A1:O1000'  # 읽고자 하는 시트와 범위 설정

# Kafka 설정
KAFKA_BROKER = 'localhost:9092'  # Kafka 브로커 주소
KAFKA_TOPIC = 'delivery_status'  # 사용할 Kafka 토픽 이름


# Google Sheets API로 데이터 가져오기
def get_google_sheets_data():
    # 자격 증명 설정
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # 데이터 읽기
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    return values


# Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # 데이터를 JSON으로 직렬화
)


# 데이터를 Kafka로 전송하는 함수
def send_data_to_kafka(data):
    headers = data[0]  # 첫 번째 행은 헤더로 가정
    for row in data[1:]:
        # 데이터 가공: 헤더와 데이터를 매핑하여 딕셔너리 생성
        message = dict(zip(headers, row))
        # Kafka로 데이터 전송
        producer.send(KAFKA_TOPIC, message)
        print(f'Sent to Kafka: {message}')


# 메인 실행
if __name__ == "__main__":
    data = get_google_sheets_data()  # Google Sheets에서 데이터 가져오기
    if data:
        send_data_to_kafka(data)  # 데이터를 Kafka로 전송
    else:
        print('No data found in Google Sheets.')
