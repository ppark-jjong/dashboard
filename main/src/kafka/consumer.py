import json
import pandas as pd

from datetime import datetime
from confluent_kafka import Consumer, KafkaError
from src.config.config_manager import ConfigManager

from src.config.logger import Logger

logger = Logger.get_logger(__name__)

# Kafka Consumer 서비스
class KafkaConsumerService:
    def __init__(self, group_id='data-processing-group'):
        self.consumer = Consumer({
            'bootstrap.servers': ConfigManager.kafka.BOOTSTRAP_SERVERS,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([ConfigManager.kafka.RAW_TOPIC])  # raw_deliveries 구독
        logger.info(f"Kafka Consumer가 토픽 '{ConfigManager.kafka.RAW_TOPIC}'에 구독되었습니다.")

    #   dash에 필요한 consume 로직
    def consume_latest_data(self):
        records = []
        today = datetime.now().strftime('%Y-%m-%d')  # 오늘 날짜 (YYYY-MM-DD 형식)

        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                break  # 메시지가 없으면 종료
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Kafka Consumer 오류: {msg.error()}")
                    continue

            try:
                data = json.loads(msg.value().decode('utf-8'))
                eta_date = data.get("ETA", "").split('T')[0]  # ETA에서 날짜 추출
                if eta_date == today:  # 오늘 날짜와 비교
                    # 필요한 컬럼만 추출
                    filtered_data = {key: data.get(key, None) for key in ConfigManager.dashboard.DASHBOARD_COLUMNS}
                    records.append(filtered_data)
            except Exception as e:
                logger.error(f"메시지 처리 중 오류 발생: {e}")

        # 읽어온 데이터를 DataFrame으로 변환
        if records:
            return pd.DataFrame(records)
        else:
            return pd.DataFrame(columns=ConfigManager.dashboard.DASHBOARD_COLUMNS)

