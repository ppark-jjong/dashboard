import json
import logging
import pandas as pd

from datetime import datetime
from confluent_kafka.admin import AdminClient, NewTopic
from src.config.config_format import KafkaConfig

# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


# Kafka Producer 서비스
class KafkaProducerService:
    def __init__(self):
        self.producer = KafkaConfig.get_producer()  # Kafka Producer 초기화
        self.admin_client = AdminClient({'bootstrap.servers': KafkaConfig.BOOTSTRAP_SERVERS})
        self.create_raw_topic()


    async def kafka_produce_async(self, data, topic):
        try:
            # DataFrame이 전달된 경우 처리
            if hasattr(data, "to_dict"):
                # DataFrame을 리스트(dict)로 변환
                data = data.to_dict(orient='records')

            # Timestamp 변환 (모든 데이터가 리스트(dict)로 변환된 상태)
            data = [self.convert_timestamps(record) for record in data]

            # Kafka 전송
            for record in data:
                self.producer.produce(topic, value=json.dumps(record), callback=self.delivery_report)

            # Kafka 버퍼 플러시
            self.producer.flush()
            logger.info(f"Kafka 토픽 '{topic}'에 비동기 전송 완료")

        except Exception as e:
            logger.error(f"Kafka 비동기 전송 실패: {e}")

    def convert_timestamps(self, record):
        for key, value in record.items():
            if isinstance(value, pd.Timestamp):  # Timestamp 객체인 경우
                record[key] = value.isoformat()  # ISO 8601 형식으로 변환
            elif isinstance(value, datetime):  # 일반 datetime 객체도 변환
                record[key] = value.isoformat()
        return record

    @staticmethod
    def delivery_report(err, msg):
        # Kafka 메시지 전송 결과 로그
        if err is not None:
            logger.error(f"메시지 전송 실패: {err}")
        else:
            logger.info(f"메시지 전송 성공: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

#   raw_deliveries 토픽을 생성
    def create_raw_topic(self):
        topic_name = KafkaConfig.RAW_TOPIC
        existing_topics = self.admin_client.list_topics(timeout=5).topics

        if topic_name not in existing_topics:
            new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
            self.admin_client.create_topics([new_topic])
            logging.info(f"Kafka 토픽 '{topic_name}'이 생성되었습니다.")
        else:
            logging.info(f"Kafka 토픽 '{topic_name}'이 이미 존재합니다.")
