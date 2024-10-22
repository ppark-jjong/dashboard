import json
import logging
from confluent_kafka import Producer, KafkaError
from src.config.config_manager import ConfigManager

config = ConfigManager()

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def create_kafka_producer():
    """Kafka Producer 인스턴스 생성"""
    producer_config = {
        'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
        'client.id': 'google-sheets-producer'
    }
    return Producer(producer_config)

def send_to_kafka(producer, topic, data):
    """DataFrame을 Kafka로 전송"""
    if data is None or data.empty:
        logger.warning("전송할 데이터가 없습니다.")
        return

    try:
        total_records = len(data)
        logger.info(f"전송할 데이터 프레임 표본 (상위 5개 행):\n{data.head()}")
        for record in data.to_dict(orient='records'):
            producer.produce(topic, value=json.dumps(record), callback=delivery_report)
        producer.flush()
        logger.info(f"총 {total_records}개의 레코드를 Kafka 토픽 '{topic}'에 전송했습니다.")
    except KafkaError as e:
        logger.error(f"Kafka 전송 중 오류 발생: {e}")

def delivery_report(err, msg):
    """Kafka 메시지 전송 결과 콜백 함수"""
    if err is not None:
        logger.error(f"메시지 전송 실패: {err}")

