import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient
from pyspark.sql import SparkSession


class ConfigManager:
    def __init__(self):
        # Google Sheets API 설정
        self.SHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'
        self.RANGE_NAME = 'Sheet1!A1:o1000'
        self.SERVICE_ACCOUNT_FILE = 'C:/MyMain/dashboard/main/oauth/google/credentials.json'

        # Kafka 설정
        self.KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
        self.KAFKA_TOPICS = {
            'dashboard_status': 'dashboard_status',
            'monthly_volume_status': 'monthly_volume_status'
        }

        # Excel 저장 경로
        self.EXCEL_SAVE_PATH = "C:\\MyMain\\dashboard\\main\\xlsx"

    def get_sheets_service(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        return build('sheets', 'v4', credentials=credentials)

    def get_kafka_producer(self):
        return Producer({'bootstrap.servers': self.KAFKA_BOOTSTRAP_SERVERS})

    def get_kafka_admin_client(self):
        return AdminClient({'bootstrap.servers': self.KAFKA_BOOTSTRAP_SERVERS})

    def get_spark_session(self):
        return SparkSession.builder \
            .appName("KafkaProtoBufConsumer") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3") \
            .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
            .config("spark.driver.extraJavaOptions", "-Dhadoop.home.dir=" + os.environ['HADOOP_HOME']) \
            .getOrCreate()

    def get_excel_save_path(self, filename):
        if not os.path.exists(self.EXCEL_SAVE_PATH):
            os.makedirs(self.EXCEL_SAVE_PATH)
        return os.path.join(self.EXCEL_SAVE_PATH, filename)