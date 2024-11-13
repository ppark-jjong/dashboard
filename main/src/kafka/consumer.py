import json
import logging
import pandas as pd
from queue import Queue
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
        self.data_frame = pd.DataFrame(columns=DashBoardConfig.DASHBOARD_COLUMNS)
        self.data_queue = Queue()

    def preprocess_message(self, message):
        """메시지를 파싱하고 필요한 전처리를 수행."""
        data = json.loads(message)
        processed_data = {col: data.get(col, None) for col in DashBoardConfig.DASHBOARD_COLUMNS}

        # Status 업데이트 로직 및 타입 변환
        processed_data['Picked'] = (data.get('Picked') == 'O')
        processed_data['Shipped'] = (data.get('Shipped') == 'O')
        processed_data['POD'] = (data.get('POD') == 'O')

        # bool 타입으로 명시적 변환
        processed_data['Picked'] = bool(processed_data['Picked'])
        processed_data['Shipped'] = bool(processed_data['Shipped'])
        processed_data['POD'] = bool(processed_data['POD'])

        if processed_data['Picked'] and not processed_data['Shipped'] and not processed_data['POD']:
            processed_data['Status'] = 'Picked'
        elif processed_data['Picked'] and processed_data['Shipped'] and not processed_data['POD']:
            processed_data['Status'] = 'Shipped'
        elif processed_data['Picked'] and processed_data['Shipped'] and processed_data['POD']:
            processed_data['Status'] = 'Delivered'
        else:
            processed_data['Status'] = 'Pending'

        return pd.DataFrame([processed_data])

    def consume_messages(self, max_records=5):
        """Kafka에서 메시지를 소비하여 대시보드용 데이터프레임에 필요한 데이터만 추가."""
        records_consumed = 0
        while records_consumed < max_records:
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
                new_row = self.preprocess_message(msg.value().decode('utf-8'))
                self.data_frame = pd.concat([self.data_frame, new_row], ignore_index=True)
                self.data_queue.put(new_row)
                records_consumed += 1
                logger.info("DataFrame에 새로운 행 추가:\n%s", new_row)
            except Exception as e:
                logger.error(f"메시지 처리 오류: {e}")

    def get_dashboard_data(self):
        """대시보드에 표시할 DataFrame을 반환."""
        return self.data_frame.tail(5)  # 최신 5개 데이터만 반환하여 대시보드에 표시

    # def save_to_gcs(self, file_name):
    #     """현재 DataFrame을 GCS에 저장."""
    #     try:
    #         storage_client = storage.Client()
    #         bucket = storage_client.bucket(config.gcs.BUCKET_NAME)
    #         blob = bucket.blob(file_name)
    #         blob.upload_from_string(self.data_frame.to_csv(index=False), 'text/csv')
    #         logger.info(f"GCS에 {file_name} 파일로 저장 완료")
    #     except Exception as e:
    #         logger.error(f"GCS 저장 오류: {e}")
