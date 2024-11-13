import json
import logging
from datetime import datetime
from google.cloud import storage
from confluent_kafka import Consumer, KafkaError
from queue import Queue
from src.config.config_manager import ConfigManager
from src.processors.realtime_data_processor import process_data

config = ConfigManager()

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


# Kafka Consumer 인스턴스 생성
def create_kafka_consumer():
    consumer_config = {
        'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'delivery-status-group',
        'auto.offset.reset': 'earliest'
    }
    return Consumer(consumer_config)


# 전처리된 데이터를 gcs에 저장
def save_to_gcs(df, bucket_name, file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')
    logger.info(f"GCS에 {file_name} 파일로 저장 완료")

