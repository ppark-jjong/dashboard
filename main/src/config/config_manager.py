import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient
import boto3
from pyspark.sql import SparkSession

class ConfigManager:
    def __init__(self):
        # Google Sheets API 설정
        self.SHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'
        self.RANGE_NAME = 'Sheet1!A2:n637'
        # self.SERVICE_ACCOUNT_FILE = '/app/oauth/google/credentials.json'
        self.SERVICE_ACCOUNT_FILE = 'C:/MyMain/dashboard/oauth/google/credentials.json'

        # Kafka 설정
        self.KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
        self.KAFKA_TOPICS = {
            'realtime_status': 'realtime_status',
            'weekly_analysis': 'weekly_analysis',
            'monthly_analysis': 'monthly_analysis',
            'dashboard_status': 'dashboard_status',
            'monthly_volume_status': 'monthly_volume_status'
        }

        # Excel 저장 경로
        self.EXCEL_SAVE_PATH = "C:/MyMain/dashboard/main/xlsx"
        # self.EXCEL_SAVE_PATH = "/app/xlsx"

        # PySpark 설정
        self.SPARK_APP_NAME = "DeliveryAnalytics"
        self.SPARK_MASTER = "spark://spark-master:7077"
        self.SPARK_EXECUTOR_MEMORY = "2g"

        # AWS S3 설정
        self.S3_BUCKET_NAME = "your-s3-bucket"
        self.S3_REGION = "us-east-1"

    def get_sheets_service(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        return build('sheets', 'v4', credentials=credentials)

    def get_kafka_producer(self):
        return Producer({'bootstrap.servers': self.KAFKA_BOOTSTRAP_SERVERS})

    def get_kafka_admin_client(self):
        return AdminClient({'bootstrap.servers': self.KAFKA_BOOTSTRAP_SERVERS})

    def get_excel_save_path(self, filename):
        if not os.path.exists(self.EXCEL_SAVE_PATH):
            os.makedirs(self.EXCEL_SAVE_PATH)
        return os.path.join(self.EXCEL_SAVE_PATH, filename)

    def get_s3_client(self):
        return boto3.client('s3', region_name=self.S3_REGION)

    def get_spark_session(self):
        return SparkSession.builder \
            .appName(self.SPARK_APP_NAME) \
            .master(self.SPARK_MASTER) \
            .config("spark.executor.memory", self.SPARK_EXECUTOR_MEMORY) \
            .getOrCreate()
