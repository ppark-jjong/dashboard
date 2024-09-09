from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from kafka import KafkaProducer
import json

# Google Sheets API 설정
SPREADSHEET_ID = 'parkjonghyeok2000@gmail.com'  # Google Sheets의 ID를 입력하세요
RANGE_NAME = 'Sheet1!A1:D10'  # 읽고 싶은 범위 설정

# Kafka 설정
KAFKA_BROKER = 'localhost:9092'  # Kafka 브로커 주소
KAFKA_TOPIC = 'delivery_status'  # 전송할 Kafka 토픽 이름

# 자격 증명 파일 로드
creds = Credentials.from_service_account_file('credentials.json')
service = build('sheets', 'v4', credentials=creds)

# Google Sheets 데이터 가져오기
def get_google_sheets_data():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    return values

# Kafka 프로듀서 설정
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Kafka로 데이터 전송
def send_data_to_kafka(data):
    for row in data:
        # 필요한 경우 데이터 가공
        message = {
            'order_id': row[0],
            'status': row[1],
            'timestamp': row[2],
            'location': row[3]
        }
        producer.send(KAFKA_TOPIC, message)
        print(f'Sent to Kafka: {message}')

if __name__ == "__main__":
    # Google Sheets에서 데이터 가져오기
    data = get_google_sheets_data()
    if data:
        # 첫 번째 행이 헤더라면 건너뛰기
        send_data_to_kafka(data[1:])
    else:
        print('No data found in Google Sheets.')
