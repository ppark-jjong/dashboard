from consumer import DeliveryProducer, start_spark_consumer
from multiprocessing import Process
import time


# Producer 실행 함수
def run_producer():
    print("Producer를 시작합니다...")
    producer = DeliveryProducer()
    producer.process_and_send_data()
    producer.close()


# Spark Consumer 실행 함수
def run_consumer():
    print("Spark Consumer를 시작합니다...")
    start_spark_consumer()


# 메인 함수에서 두 프로세스를 실행
if __name__ == "__main__":
    print("Google Sheets 배송 데이터 분석 및 전송을 시작합니다...")

    # Producer 프로세스 실행
    producer_process = Process(target=run_producer)
    producer_process.start()

    # Producer가 데이터를 전송할 시간을 주기 위해 잠시 대기
    time.sleep(5)

    # Consumer 프로세스 실행
    consumer_process = Process(target=run_consumer)
    consumer_process.start()

    # 두 프로세스가 완료될 때까지 대기
    producer_process.join()
    consumer_process.join()
