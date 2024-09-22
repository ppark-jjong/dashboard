import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from kafka import KafkaProducer
import delivery_pb2  # ProtoBuf에서 생성된 코드
import json

# Google Sheets API 설정
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# 스프레드시트 ID와 범위 설정
SPREADSHEET_ID = 'your_spreadsheet_id'
RANGE_NAME = 'Sheet1!A1:E'

def get_sheet_data():
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return pd.DataFrame()
    else:
        # 첫 번째 행을 컬럼명으로 사용하여 DataFrame 생성
        df = pd.DataFrame(values[1:], columns=values[0])
        return df

def preprocess_data(data):
    data['Date(접수일)'] = pd.to_datetime(data['Date(접수일)'])
    data['Week'] = data['Date(접수일)'].dt.to_period('W')
    data['Weekday'] = data['Date(접수일)'].dt.day_name()
    data['Completed'] = data['Status'] == 'Completed'
    return data

def send_to_kafka(data):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    for _, row in data.iterrows():
        delivery = delivery_pb2.DeliveryData()
        delivery.date = row['Date(접수일)'].strftime('%Y-%m-%d')
        delivery.status = row['Status']
        delivery.billed_distance = float(row['Billed Distance (Put into system)']) if row['Billed Distance (Put into system)'] else 0.0
        delivery.issue = row['issue']

        message = delivery.SerializeToString()
        producer.send('delivery_topic', message)

    producer.flush()
    producer.close()

if __name__ == '__main__':
    data = get_sheet_data()
    if not data.empty:
        data = preprocess_data(data)
        send_to_kafka(data)
        print("Kafka로 데이터 전송 완료.")
    else:
        print("데이터가 없습니다.")
