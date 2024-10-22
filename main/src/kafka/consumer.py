import json
import logging
from confluent_kafka import Consumer, KafkaError
from src.config.config_manager import ConfigManager
from queue import Queue
import pandas as pd

config = ConfigManager()

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def create_kafka_consumer():
    """Kafka Consumer 인스턴스 생성"""
    consumer_config = {
        'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'delivery-status-group',
        'auto.offset.reset': 'earliest'
    }
    return Consumer(consumer_config)

def consume_messages(topic, message_queue: Queue):
    """Kafka로부터 메시지를 수신하여 처리"""
    consumer = create_kafka_consumer()
    consumer.subscribe([topic])
    logger.info(f"'{topic}' 토픽으로부터 메시지를 수신합니다.")

    received_records = []
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
            received_records.append(message)
            message_queue.put(message)
            logger.info(f"수신한 메시지: {message}")

            if len(received_records) >= 5:
                df = pd.DataFrame(received_records)
                logger.info(f"수신한 데이터 프레임 표본 (상위 5개 행):\n{df.head()}")
                received_records = []

    except KeyboardInterrupt:
        logger.info("메시지 소비를 중단합니다.")
    finally:
        consumer.close()
        logger.info("Kafka Consumer 연결을 종료합니다.")
