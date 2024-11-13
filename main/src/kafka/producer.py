import json
import logging
from confluent_kafka import Producer
from src.config.config_manager import ConfigManager

config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class KafkaProducerService:
    def __init__(self):
        self.producer = Producer({'bootstrap.servers': config.kafka.BOOTSTRAP_SERVERS})

    # Kafka Producer 인스턴스 생성
    def create_kafka_producer(self):
        producer_config = {
            'bootstrap.servers': config.kafka.BOOTSTRAP_SERVERS,
            'client.id': 'google-sheets-producer'
        }
        return Producer(producer_config)

    def send_data(self, data):
        if data.empty:
            logger.warning("전송할 데이터가 비어있습니다. 데이터 내용: %s", data.to_dict())
            return

        topic = config.kafka.TOPICS['dashboard_status']
        try:
            for record in data.to_dict(orient='records'):
                self.producer.produce(topic, value=json.dumps(record), callback=self.delivery_report)
            self.producer.flush()
            logger.info(f"{len(data)}개의 레코드를 Kafka 토픽 '{topic}'에 전송했습니다.")
        except Exception as e:
            logger.error(f"Kafka 전송 실패: {e}")

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            logger.error(f"메시지 전송 실패: {err}")
        else:
            logger.info(f"메시지 전송 성공: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")
