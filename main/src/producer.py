from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
import json
import pandas as pd
from datetime import datetime

# Google Sheets API 설정
SERVICE_ACCOUNT_FILE = 'C:\MyMain\oauth\google\credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'
RANGE_NAME = 'Sheet1!A:Z'  # 모든 열을 읽도록 설정


class DeliveryProducer:
    def __init__(self, broker='localhost:29092', topic='delivery-data'):
        self.broker = broker
        self.topic = topic
        self.create_topic()
        self.producer = KafkaProducer(
            bootstrap_servers=[self.broker],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        self.setup_google_sheets()

    # Kafka 토픽 생성
    def create_topic(self):
        admin_client = KafkaAdminClient(bootstrap_servers=[self.broker])
        topic_list = []
        topic_list.append(NewTopic(name=self.topic, num_partitions=1, replication_factor=1))
        try:
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print(f"토픽 '{self.topic}'이 생성되었습니다.")
        except TopicAlreadyExistsError:
            print(f"토픽 '{self.topic}'이 이미 존재합니다.")
        finally:
            admin_client.close()

    # Google Sheets API 설정
    def setup_google_sheets(self):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)

    # Google Sheets 데이터 가져오기
    def fetch_sheet_data(self):
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])
        return values

    # 데이터 전처리
    def preprocess_data(self, data):
        df = pd.DataFrame(data[1:], columns=data[0])  # 첫 번째 행을 헤더로 사용

        # 날짜 처리
        df['Date(접수일)'] = pd.to_datetime(df['Date(접수일)'], errors='coerce')
        df['Week'] = df['Date(접수일)'].dt.to_period('W')
        df['Weekday'] = df['Date(접수일)'].dt.day_name()

        # 'Completed' 상태 처리
        df['Completed'] = df['Status'] == 'Completed'

        # 숫자 데이터 처리
        numeric_columns = ['Billed Distance (Put into system)', 'DPS#']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 'issue' 열 처리
        if 'issue' in df.columns:
            df['issue'] = df['issue'].fillna('')  # NaN 값을 빈 문자열로 대체

        return df

    # 일별 분석
    def daily_analysis(self, data, date):
        daily_data = data[data['Date(접수일)'].dt.date == date]
        status_counts = daily_data['Status'].value_counts().to_dict()
        completion_rate = daily_data['Completed'].mean() * 100 if not daily_data.empty else 0
        avg_distance = daily_data[
            'Billed Distance (Put into system)'].mean() if 'Billed Distance (Put into system)' in daily_data.columns else 0
        issue_count = daily_data['issue'].eq('O').sum() if 'issue' in daily_data.columns else 0
        return status_counts, completion_rate, avg_distance, issue_count

    # 주별 분석
    def weekly_analysis(self, data, week):
        weekly_data = data[data['Week'] == week]
        completion_rate = weekly_data['Completed'].mean() * 100 if not weekly_data.empty else 0
        avg_distance = weekly_data[
            'Billed Distance (Put into system)'].mean() if 'Billed Distance (Put into system)' in weekly_data.columns else 0
        issue_count = weekly_data['issue'].eq('O').sum() if 'issue' in weekly_data.columns else 0
        return completion_rate, avg_distance, issue_count

    # 이슈 발생 패턴 분석
    def analyze_issue_pattern(self, data):
        if 'issue' in data.columns and 'Weekday' in data.columns:
            issue_pattern = data[data['issue'] == 'O'].groupby('Weekday')['DPS#'].count().to_dict()
        else:
            issue_pattern = {}
        return issue_pattern

    # 데이터를 Kafka로 전송
    def send_data(self, data):
        self.producer.send(self.topic, value=data)
        print(f"Kafka로 데이터를 전송했습니다: {data}")

    # Google Sheets 데이터 처리 및 Kafka로 전송
    def process_and_send_data(self):
        sheet_data = self.fetch_sheet_data()
        if sheet_data:
            print('Google Sheets에서 데이터를 가져왔습니다.')
            df = self.preprocess_data(sheet_data)

            today = datetime.now().date()
            this_week = pd.Timestamp(today).to_period('W')

            # 일별 분석
            daily_stats = self.daily_analysis(df, today)
            daily_data = {
                "type": "daily",
                "date": str(today),
                "status_counts": daily_stats[0],
                "completion_rate": float(daily_stats[1]),
                "avg_distance": float(daily_stats[2]),
                "issue_count": int(daily_stats[3])
            }
            self.send_data(daily_data)

            # 주별 분석
            weekly_stats = self.weekly_analysis(df, this_week)
            weekly_data = {
                "type": "weekly",
                "week": str(this_week),
                "completion_rate": float(weekly_stats[0]),
                "avg_distance": float(weekly_stats[1]),
                "issue_count": int(weekly_stats[2])
            }
            self.send_data(weekly_data)

            # 이슈 패턴 분석
            issue_pattern = self.analyze_issue_pattern(df)
            issue_data = {
                "type": "issue_pattern",
                "issue_pattern": issue_pattern
            }
            self.send_data(issue_data)
        else:
            print('Google Sheets에서 데이터를 찾을 수 없습니다.')

    # 프로듀서 연결 종료
    def close(self):
        self.producer.flush()
        self.producer.close()


# DeliveryProducer 객체 생성
def create_producer():
    return DeliveryProducer()
