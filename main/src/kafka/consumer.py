from google.cloud import storage
from confluent_kafka import Consumer, KafkaError
from queue import Queue
from src.config.config_manager import ConfigManager
from src.processors.realtime_data_processor import process_data
import json
import logging
from datetime import datetime
import pandas as pd

config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def create_kafka_consumer():
    consumer_config = {
        'bootstrap.servers': config.kafka.BOOTSTRAP_SERVERS,
        'group.id': 'delivery-status-group',
        'auto.offset.reset': 'earliest'
    }
    return Consumer(consumer_config)

def save_to_gcs(df, bucket_name, file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')
    logger.info(f"GCS에 {file_name} 파일로 저장 완료")

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

            if len(records) >= 10:
                today_data, future_data = process_data(records)

                for record in today_data.to_dict(orient='records'):
                    message_queue.put(record)

                if not future_data.empty:
                    file_name = f"future_eta_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                    save_to_gcs(future_data, config.gcs.BUCKET_NAME, file_name)

                records = []

    except KeyboardInterrupt:
        logger.info("메시지 소비를 중단합니다.")
    finally:
        consumer.close()
        logger.info("Kafka Consumer 연결을 종료합니다.")
