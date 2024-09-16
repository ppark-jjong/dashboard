import time
import threading
from producer import DeliveryProducer
from consumer import start_consumer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def start_producer(interval=300):
    producer = DeliveryProducer()
    try:
        while True:
            logger.info("Producer: 데이터 수집 및 Kafka 전송 작업을 시작합니다...")
            producer.process_and_send_data()
            logger.info("Producer: 데이터 수집 및 전송 작업이 완료되었습니다.")
            next_run = time.time() + interval
            logger.info(f"Producer: 다음 실행 시간: {time.ctime(next_run)}")
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Producer: 사용자에 의해 중단되었습니다.")
    finally:
        logger.info("Producer: 종료합니다.")
        producer.close()


def run_consumer():
    logger.info("Consumer: 시작합니다.")
    try:
        start_consumer()
    except Exception as e:
        logger.error(f"Consumer: 오류 발생 - {e}")
    finally:
        logger.info("Consumer: 종료합니다.")


if __name__ == "__main__":
    logger.info("Google Sheets 배송 데이터 분석 및 전송 시스템을 시작합니다...")

    # Consumer 스레드 시작
    consumer_thread = threading.Thread(target=run_consumer)
    consumer_thread.start()

    # Producer 실행 (메인 스레드)
    try:
        start_producer()
    except KeyboardInterrupt:
        logger.info("메인 프로그램: 사용자에 의해 중단되었습니다.")

    # Consumer 스레드 종료 대기
    logger.info("Consumer 스레드 종료를 기다리는 중...")
    consumer_thread.join()

    logger.info("프로그램을 종료합니다.")