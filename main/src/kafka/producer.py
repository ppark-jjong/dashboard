import json
import logging
from confluent_kafka import Producer, KafkaError
from src.config.config_manager import ConfigManager

# 설정 불러오기 및 로거 설정
config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


# Kafka Producer 인스턴스 생성
def create_kafka_producer():
    producer_config = {
        'bootstrap.servers': config.kafka.BOOTSTRAP_SERVERS,
        'client.id': 'google-sheets-producer'
    }
    return Producer(producer_config)


# DataFrame을 Kafka로 전송
def send_to_kafka(producer, topic, data):
    """
    DataFrame 데이터를 Kafka로 전송
    Args:
        producer (Producer): Kafka Producer 인스턴스
        topic (str): Kafka 토픽 이름
        data (pd.DataFrame): 전송할 데이터프레임
    """
    if data is None or data.empty:
        logger.warning("전송할 데이터가 없습니다.")
        return

    total_records = len(data)
    logger.info(f"전송할 데이터 프레임 표본 (상위 5개 행):\n{data.head()}")

    try:
        # DataFrame의 각 행을 JSON 형식으로 변환하여 Kafka로 전송
        for record in data.to_dict(orient='records'):
            producer.produce(topic, value=json.dumps(record), callback=delivery_report)

        # 메시지 전송이 완료될 때까지 대기
        producer.flush()
        logger.info(f"총 {total_records}개의 레코드를 Kafka 토픽 '{topic}'에 전송했습니다.")
    except KafkaError as e:
        logger.error(f"Kafka 전송 중 오류 발생: {e}")


# Kafka 메시지 전송 결과 콜백 함수
def delivery_report(err, msg):
    if err is not None:
        logger.error(f"메시지 전송 실패: {err}")
    else:
        logger.info(f"메시지 전송 성공: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")
