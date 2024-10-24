import json
import logging
from datetime import datetime

from confluent_kafka import Consumer, KafkaError
from queue import Queue
from src.config.config_manager import ConfigManager
from src.processors.realtime_data_processor import process_data
from google.cloud import storage
import pandas as pd

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


# 전처리된 데이터를 GCS에 저장
def save_to_gcs(df, bucket_name, file_name):
    storage_client = storage.Client.from_service_account_json(config.SERVICE_ACCOUNT_FILE)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # DataFrame을 CSV로 저장한 후 업로드
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')
    logger.info(f"GCS에 {file_name} 파일로 저장 완료")

# Kafka 메시지를 수신하고 전처리 후 GCS와 Dash로 전달
def consume_and_process_messages(topic, message_queue: Queue):
    consumer = create_kafka_consumer()
    consumer.subscribe([topic])
    logger.info(f"'{topic}' 토픽에서 메시지를 수신합니다.")

    records = []

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info(f"토픽의 마지막 메시지에 도달했습니다: {msg.topic()} [{msg.partition()}]")
                else:
                    logger.error(f"Consumer 오류: {msg.error()}")
                continue

            message_value = msg.value().decode('utf-8')
            message = json.loads(message_value)
            records.append(message)

            # 일정량의 메시지가 누적되면 처리
            if len(records) >= 10:
                today_data, future_data = process_data(records)

                # 오늘 데이터는 실시간 대시보드에 전달
                for record in today_data.to_dict(orient='records'):
                    message_queue.put(record)  # 실시간 데이터 대기열에 추가 (Dash로 전달)

                # 미래 데이터는 GCS에 저장
                if not future_data.empty:
                    file_name = f"future_eta_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                    save_to_gcs(future_data, config.S3_BUCKET_NAME, file_name)

                records = []  # 기록 초기화

    except KeyboardInterrupt:
        logger.info("메시지 소비를 중단합니다.")
    finally:
        consumer.close()
        logger.info("Kafka Consumer 연결을 종료합니다.")
