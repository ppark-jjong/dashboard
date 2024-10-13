import threading
import logging
from producer import KafkaProducer
from googleApi import get_sheet_data, preprocess_data
from consumer import start_spark_consumer
from config_manager import ConfigManager

config = ConfigManager()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def producer_task():
    try:
        producer = KafkaProducer()
        data_list = get_sheet_data()
        if data_list:
            # 데이터 전처리
            dashboard_data, monthly_volume_data = preprocess_data(data_list)
            # Kafka에 데이터 전송
            producer.send_to_kafka(config.KAFKA_TOPICS['dashboard_status'], dashboard_data)
            producer.send_to_kafka(config.KAFKA_TOPICS['monthly_volume_status'], monthly_volume_data)
        producer.flush()
        logger.info("Producer 작업 완료")
    except Exception as e:
        logger.error(f"Producer 작업 중 오류 발생: {e}")

if __name__ == "__main__":
    try:
        # Producer 작업 실행
        logger.info("Producer 작업을 시작합니다.")
        producer_task()

        # PySpark Consumer 실행 (별도 스레드)
        logger.info("PySpark Consumer 작업을 시작합니다.")
        consumer_thread = threading.Thread(target=start_spark_consumer)
        consumer_thread.start()

        # 스레드가 완료될 때까지 기다림
        consumer_thread.join()
        logger.info("PySpark Consumer 작업 완료")
    except Exception as e:
        logger.error(f"메인 실행 중 오류 발생: {e}")