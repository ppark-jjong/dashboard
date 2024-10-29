# src/tests/test_google_sheets_kafka.py
import logging

from confluent_kafka import KafkaError

from src.collectors.google_sheets import collect_and_send_data
from src.brokers.kafka.consumer import create_kafka_consumer
from src.config.config_manager import ConfigManager
from queue import Queue
import time

config = ConfigManager()

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Google Sheets 데이터를 수집하고 Kafka로 전송한 후, 데이터를 소비하여 확인
def test_google_sheets_to_kafka():
    # Step 1: Google Sheets 데이터 수집 및 Kafka 전송
    collect_and_send_data()
    logger.info("Google Sheets 데이터를 Kafka로 전송 완료.")

    # Step 2: Kafka에서 데이터 수신 테스트
    topic = config.KAFKA_TOPICS['realtime_status']
    message_queue = Queue()
    consumer = create_kafka_consumer()
    consumer.subscribe([topic])
    logger.info(f"'{topic}' 토픽으로부터 데이터를 수신합니다.")

    received_messages = []

    try:
        end_time = time.time() + 10  # 10초 동안 메시지 수신 시도
        while time.time() < end_time and len(received_messages) < 5:
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
            received_messages.append(message_value)
            logger.info(f"수신한 메시지: {message_value}")

    except Exception as e:
        logger.error(f"Kafka 메시지 수신 중 오류 발생: {e}")
    finally:
        consumer.close()
        logger.info("Kafka Consumer 연결을 종료합니다.")

    # 테스트 결과 확인
    if received_messages:
        logger.info(f"총 {len(received_messages)}개의 메시지를 수신했습니다.")
    else:
        logger.error("수신된 메시지가 없습니다.")

# 실제로 테스트를 실행하는 코드 블록
if __name__ == "__main__":
    test_google_sheets_to_kafka()
