import json
import logging
from confluent_kafka import Producer
from src.config.config_data_format import KafkaConfig

# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


# Kafka Producer 서비스
class KafkaProducerService:
    def __init__(self):
        self.producer = KafkaConfig.get_producer()  # Kafka Producer 초기화

    async def kafka_produce_async(self, data, topic):
        # 비동기 방식으로 데이터 전송 (DataFrame 또는 Dictionary)
        try:
            if isinstance(data, dict):  # 단일 레코드
                self.producer.produce(topic, value=json.dumps(data), callback=self.delivery_report)
            elif isinstance(data, list):  # 다중 레코드 (리스트 형태)
                for record in data:
                    self.producer.produce(topic, value=json.dumps(record), callback=self.delivery_report)
            else:  # DataFrame 처리
                for record in data.to_dict(orient='records'):
                    self.producer.produce(topic, value=json.dumps(record), callback=self.delivery_report)

            self.producer.flush()
            logger.info(f"Kafka 토픽 '{topic}'에 비동기 전송 완료")
        except Exception as e:
            logger.error(f"Kafka 비동기 전송 실패: {e}")


    @staticmethod
    def delivery_report(err, msg):
        # Kafka 메시지 전송 결과 로그
        if err is not None:
            logger.error(f"메시지 전송 실패: {err}")
        else:
            logger.info(f"메시지 전송 성공: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")
