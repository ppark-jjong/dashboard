from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, FloatType, IntegerType
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json
import pandas as pd
from datetime import datetime

# Google Sheets API 설정
SERVICE_ACCOUNT_FILE = 'C:/MyMain/oauth/google/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'
RANGE_NAME = 'Sheet1!A:Z'  # 모든 열을 읽도록 설정

# Kafka 설정
BROKER = 'localhost:29092'
TOPIC = 'delivery-data'

# Kafka Producer 및 토픽 생성 설정
class DeliveryProducer:
    def __init__(self, broker=BROKER, topic=TOPIC):
        self.broker = broker
        self.topic = topic
        self.create_topic()
        self.producer = KafkaProducer(
            bootstrap_servers=[self.broker],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        self.setup_google_sheets()

    def create_topic(self):
        admin_client = KafkaAdminClient(bootstrap_servers=[self.broker])
        topic_list = [NewTopic(name=self.topic, num_partitions=1, replication_factor=1)]
        try:
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print(f"토픽 '{self.topic}'이 생성되었습니다.")
        except TopicAlreadyExistsError:
            print(f"토픽 '{self.topic}'이 이미 존재합니다.")
        finally:
            admin_client.close()

    def setup_google_sheets(self):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)

    def fetch_sheet_data(self):
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])
        return values

    def preprocess_data(self, data):
        df = pd.DataFrame(data[1:], columns=data[0])
        df['Date(접수일)'] = pd.to_datetime(df['Date(접수일)'], errors='coerce')
        df['Week'] = df['Date(접수일)'].dt.to_period('W')
        df['Weekday'] = df['Date(접수일)'].dt.day_name()
        df['Completed'] = df['Status'] == 'Completed'
        numeric_columns = ['Billed Distance (Put into system)', 'DPS#']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        if 'issue' in df.columns:
            df['issue'] = df['issue'].fillna('')
        return df

    def daily_analysis(self, data, date):
        daily_data = data[data['Date(접수일)'].dt.date == date]
        status_counts = daily_data['Status'].value_counts().to_dict()
        completion_rate = daily_data['Completed'].mean() * 100 if not daily_data.empty else 0
        avg_distance = daily_data['Billed Distance (Put into system)'].mean() if 'Billed Distance (Put into system)' in daily_data.columns else 0
        issue_count = daily_data['issue'].eq('O').sum() if 'issue' in daily_data.columns else 0
        return status_counts, completion_rate, avg_distance, issue_count

    def weekly_analysis(self, data, week):
        weekly_data = data[data['Week'] == week]
        completion_rate = weekly_data['Completed'].mean() * 100 if not weekly_data.empty else 0
        avg_distance = weekly_data['Billed Distance (Put into system)'].mean() if 'Billed Distance (Put into system)' in weekly_data.columns else 0
        issue_count = weekly_data['issue'].eq('O').sum() if 'issue' in weekly_data.columns else 0
        return completion_rate, avg_distance, issue_count

    def analyze_issue_pattern(self, data):
        if 'issue' in data.columns and 'Weekday' in data.columns:
            issue_pattern = data[data['issue'] == 'O'].groupby('Weekday')['DPS#'].count().to_dict()
        else:
            issue_pattern = {}
        return issue_pattern

    def send_data(self, data):
        self.producer.send(self.topic, value=data)
        print(f"Kafka로 데이터를 전송했습니다: {data}")

    def process_and_send_data(self):
        sheet_data = self.fetch_sheet_data()
        if sheet_data:
            print('Google Sheets에서 데이터를 가져왔습니다.')
            df = self.preprocess_data(sheet_data)
            today = datetime.now().date()
            this_week = pd.Timestamp(today).to_period('W')

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

            weekly_stats = self.weekly_analysis(df, this_week)
            weekly_data = {
                "type": "weekly",
                "week": str(this_week),
                "completion_rate": float(weekly_stats[0]),
                "avg_distance": float(weekly_stats[1]),
                "issue_count": int(weekly_stats[2])
            }
            self.send_data(weekly_data)

            issue_pattern = self.analyze_issue_pattern(df)
            issue_data = {
                "type": "issue_pattern",
                "issue_pattern": issue_pattern
            }
            self.send_data(issue_data)
        else:
            print('Google Sheets에서 데이터를 찾을 수 없습니다.')

    def close(self):
        self.producer.flush()
        self.producer.close()

# Spark Streaming Consumer
def start_spark_consumer():
    spark = SparkSession.builder \
        .appName("DeliveryDataConsumer") \
        .getOrCreate()

    kafka_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "delivery-data") \
        .load()

    schema = StructType() \
        .add("type", StringType()) \
        .add("date", StringType()) \
        .add("week", StringType()) \
        .add("status_counts", StringType()) \
        .add("completion_rate", FloatType()) \
        .add("avg_distance", FloatType()) \
        .add("issue_count", IntegerType()) \
        .add("issue_pattern", StringType())

    delivery_data = kafka_stream.selectExpr("CAST(value AS STRING) as json") \
        .select(from_json(col("json"), schema).alias("data")) \
        .select("data.*")

    query = delivery_data.writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    query.awaitTermination()

# 실행: Producer와 Consumer
if __name__ == "__main__":
    print("Google Sheets 배송 데이터 분석 및 전송을 시작합니다...")
    producer = DeliveryProducer()
    producer.process_and_send_data()
    producer.close()

    print("Spark Consumer를 시작합니다...")
    start_spark_consumer()
