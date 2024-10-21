import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient
import boto3
from pyspark.sql import SparkSession
from selenium import webdriver
from typing import Dict, Any

class ConfigManager:
    def __init__(self):
        # Google Sheets API 설정
        self.SHEET_ID = '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc'
        self.RANGE_NAME = 'Sheet1!A2:n637'
        self.SERVICE_ACCOUNT_FILE = 'C:/MyMain/dashboard/main/oauth/google/credentials.json'

        # Kafka 설정
        self.KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
        self.KAFKA_TOPICS = {
            'realtime_status': 'realtime_status',
            'weekly_analysis': 'weekly_analysis',
            'monthly_analysis': 'monthly_analysis',
            'dashboard_status': 'dashboard_status',
            'monthly_volume_status': 'monthly_volume_status'
        }

        # PySpark 설정
        self.SPARK_APP_NAME = "DeliveryAnalytics"
        self.SPARK_MASTER = "spark://spark-master:7077"
        self.SPARK_EXECUTOR_MEMORY = "2g"

        # AWS S3 설정
        self.S3_BUCKET_NAME = "your-s3-bucket"
        self.S3_REGION = "us-east-1"

        # 웹 크롤링 설정
        self.DOWNLOAD_FOLDER = "C:/MyMain/dashboard/main/xlsx"
        self.WEBDRIVER_TIMEOUT = 30
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5
        self.DOWNLOAD_WAIT_TIME = 120


    def get_sheets_service(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        return build('sheets', 'v4', credentials=credentials)

    def get_kafka_producer(self):
        return Producer({'bootstrap.servers': self.KAFKA_BOOTSTRAP_SERVERS})

    def get_kafka_admin_client(self):
        return AdminClient({'bootstrap.servers': self.KAFKA_BOOTSTRAP_SERVERS})

    def get_s3_client(self):
        return boto3.client('s3', region_name=self.S3_REGION)

    def get_spark_session(self):
        return SparkSession.builder \
            .appName(self.SPARK_APP_NAME) \
            .master(self.SPARK_MASTER) \
            .config("spark.executor.memory", self.SPARK_EXECUTOR_MEMORY) \
            .getOrCreate()

#        Selenium WebDriver 설정을 초기화합니다.
    def get_web_driver(self) -> webdriver.Chrome:
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.DOWNLOAD_FOLDER,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=chrome_options)

# 웹 크롤러에 필요한 설정을 반환합니다.
    def get_web_crawler_config(self) -> Dict[str, Any]:
        return {
            "DOWNLOAD_FOLDER": self.DOWNLOAD_FOLDER,
            "WEBDRIVER_TIMEOUT": self.WEBDRIVER_TIMEOUT,
            "MAX_RETRIES": self.MAX_RETRIES,
            "RETRY_DELAY": self.RETRY_DELAY,
            "DOWNLOAD_WAIT_TIME": self.DOWNLOAD_WAIT_TIME
        }
