import json
import logging
import pandas as pd
from confluent_kafka import Consumer, KafkaError
from src.config.config_manager import ConfigManager
from src.config.data_format import DashBoardConfig

# 설정 로드 및 로그 설정
config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self, topic, group_id='delivery-status-group'):
        self.topic = topic
        self.consumer = Consumer({
            'bootstrap.servers': config.kafka.BOOTSTRAP_SERVERS,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([topic])
        logger.info(f"Subscribed to topic: {self.topic}")

    def preprocess_message(self, message):
        """메시지를 파싱하고 필요한 전처리를 수행."""
        data = json.loads(message)
        processed_data = {col: data.get(col, None) for col in DashBoardConfig.DASHBOARD_COLUMNS}

        # Status 필드를 변환
        processed_data['Picked'], processed_data['Shipped'], processed_data['POD'] = \
            self.convert_to_bool(data, ['Picked', 'Shipped', 'POD'])
        processed_data['Status'] = self.determine_status(processed_data)

        # 명시적으로 bool 타입으로 변환
        processed_data['Picked'] = bool(processed_data['Picked'])
        processed_data['Shipped'] = bool(processed_data['Shipped'])
        processed_data['POD'] = bool(processed_data['POD'])

        return pd.DataFrame([processed_data])

    @staticmethod
    def convert_to_bool(data, fields):
        """주어진 필드를 bool 타입으로 변환"""
        return [(data.get(field) == 'O') for field in fields]

    @staticmethod
    def determine_status(data):
        """Status 상태를 결정"""
        if data['Picked'] and not data['Shipped'] and not data['POD']:
            return 'Picked'
        elif data['Picked'] and data['Shipped'] and not data['POD']:
            return 'Shipped'
        elif data['Picked'] and data['Shipped'] and data['POD']:
            return 'Delivered'
        return 'Pending'

    def consume_messages(self, max_records=5):
        """Kafka에서 메시지를 소비하여 DataFrame으로 반환."""
        records = []
        while len(records) < max_records:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info("Kafka 파티션 끝")
                else:
                    logger.error(f"Kafka Consumer 오류: {msg.error()}")
                continue

            try:
                records.append(self.preprocess_message(msg.value().decode('utf-8')))
            except Exception as e:
                logger.error(f"메시지 처리 오류: {e}")

        return pd.concat(records, ignore_index=True) if records else pd.DataFrame(columns=DashBoardConfig.DASHBOARD_COLUMNS)
