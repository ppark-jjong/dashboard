import json
import logging
from datetime import datetime

import pandas as pd
from confluent_kafka import Producer, KafkaError
from src.config.config_manager import ConfigManager

config = ConfigManager()

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


# Kafka Producer 생성 함수
def create_kafka_producer():
    """Confluent Kafka Producer를 생성하는 함수"""
    producer_config = {
        'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
        'client.id': 'google-sheets-producer'
    }
    return Producer(producer_config)


# Kafka 토픽의 존재 여부를 확인하는 함수
def ensure_topic_exists(topic):
    """Kafka 토픽이 존재하지 않으면 생성하는 함수"""
    logger.info(f"'{topic}' 토픽에 데이터를 전송합니다. 필요한 경우 Kafka Admin을 통해 토픽을 생성해주세요.")


# Kafka로 데이터 전송 함수
def send_to_kafka(producer, topic, data):
    """
    데이터를 Kafka로 전송하는 함수

    Args:
        producer (Producer): Kafka Producer 인스턴스
        topic (str): 전송할 Kafka 토픽 이름
        data (DataFrame): 전송할 데이터
    """
    if data is None or data.empty:
        logger.warning("전송할 데이터가 없습니다.")
        return

    ensure_topic_exists(topic)

    # DataFrame을 JSON 형식으로 변환하여 Kafka로 전송
    total_records = 0  # 전송한 메시지 수를 세기 위한 변수
    try:
        for record in data.to_dict(orient='records'):
            # ETA를 날짜 및 시간 형식으로 문자열 변환
            if 'ETA' in record:
                # ETA가 datetime 형식인지 확인 후 변환
                if isinstance(record['ETA'], datetime):
                    record['ETA'] = record['ETA'].strftime('%Y-%m-%d %H:%M:%S')

            producer.produce(topic, key=str(record.get('DPS#', '')), value=json.dumps(record), callback=delivery_report)
            total_records += 1
        producer.flush()
        logger.info(f"총 {total_records}개의 레코드를 Kafka 토픽 '{topic}'에 전송했습니다.")
    except KafkaError as e:
        logger.error(f"Kafka 전송 중 오류 발생: {e}")
    except Exception as e:
        logger.error(f"데이터 전송 중 예외 발생: {e}")


# Kafka 메시지 전송 결과 콜백 함수
def delivery_report(err, msg):
    """Kafka 메시지 전송 결과를 처리하는 콜백 함수"""
    if err is not None:
        logger.error(f"메시지 전송 실패: {err}")
    # 개별 성공 메시지는 출력하지 않도록 수정하여, 총 전송 건수만 로그에 남김
