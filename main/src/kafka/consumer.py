import json
import logging
import pandas as pd

from datetime import datetime
from confluent_kafka import Consumer, KafkaError
from dash import callback

from src.config.config_data_format import KafkaConfig
from src.kafka.producer import KafkaProducerService
from src.config.config_data_format import DashBoardConfig


# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


# Kafka Consumer 서비스
class KafkaConsumerService:
    def __init__(self, group_id='data-processing-group'):
        self.consumer = Consumer({
            'bootstrap.servers': KafkaConfig.BOOTSTRAP_SERVERS,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([KafkaConfig.RAW_TOPIC])  # raw_deliveries 구독
        self.producer = KafkaProducerService()  # 파생 토픽 전송용 Kafka Producer 초기화
        logger.info(f"Kafka Consumer가 토픽 '{KafkaConfig.RAW_TOPIC}'에 구독되었습니다.")

    # 메시지를 처리하여 파생 토픽으로 전송
    def process_message(self, message):
        try:
            data = json.loads(message)

            # Regional Trends 전송
            if data.get('Zip Code'):
                regional_data = {
                    "DPS": data["DPS"],
                    "Zip Code": data["Zip Code"],
                    "Address": data["Address"],
                    "SLA": data["SLA"],
                    "Status": data["Status"],
                    "Billed Distance": data.get("Billed Distance"),
                    "Date": data.get("Date")
                }
                self.producer.kafka_produce_async(regional_data, KafkaConfig.TOPICS['regional_trends'])

            # Time Based Trends 전송
            if data.get("ETA"):
                time_based_data = {
                    "DPS": data["DPS"],
                    "Date": data["ETA"].split('T')[0],  # ETA의 날짜 부분 추출
                    "Time": data["ETA"].split('T')[1],  # ETA의 시간 부분 추출
                    "SLA": data.get("SLA"),
                    "Status": data.get("Status")
                }
                self.producer.kafka_produce_async(time_based_data, KafkaConfig.TOPICS['time_based_trends'])

            # Delivery Performance 전송
            delivery_performance_data = {
                "DPS": data["DPS"],
                "Date": data.get("Date"),
                "ETA": data.get("ETA"),
                "SLA": data.get("SLA"),
                "Status": data.get("Status"),
                "Zip Code": data.get("Zip Code"),
                "Billed Distance": data.get("Billed Distance")
            }
            self.producer.kafka_produce_async(delivery_performance_data, KafkaConfig.TOPICS['delivery_performance'])

            # Driver Delivery Trends 전송
            if data.get("Driver ID"):
                driver_data = {
                    "DPS": data["DPS"],
                    "Driver ID": data["Driver ID"],
                    "ETA": data["ETA"].split('T')[0],  # ETA에서 날짜만 추출
                    "Time": data["ETA"].split('T')[1],  # ETA에서 시간만 추출
                    "Zip Code": data.get("Zip Code"),
                    "Status": data["Status"],
                    "Billed Distance": data.get("Billed Distance"),
                    "SLA": data.get("SLA")
                }
                self.producer.kafka_produce_async(driver_data, KafkaConfig.TOPICS['driver_delivery_trends'])

        except Exception as e:
            logger.error(f"메시지 처리 중 오류 발생: {e}")


    def consume_latest_data(self):
        """
        Kafka에서 메시지를 소비하고 ETA가 오늘 날짜인 데이터만 반환
        """
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
                    filtered_data = {key: data.get(key, None) for key in DashBoardConfig.DASHBOARD_COLUMNS}
                    records.append(filtered_data)
            except Exception as e:
                logger.error(f"메시지 처리 중 오류 발생: {e}")

        # 읽어온 데이터를 DataFrame으로 변환
        if records:
            return pd.DataFrame(records)
        else:
            return pd.DataFrame(columns=DashBoardConfig.DASHBOARD_COLUMNS)
