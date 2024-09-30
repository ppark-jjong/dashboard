import threading
from producer import KafkaProducer
from googleApi import get_sheet_data, preprocess_data
from src.consumer import start_spark_consumer

def producer_task():
    try:
        producer = KafkaProducer()
        data_list = get_sheet_data()
        if data_list:
            # 데이터 전처리
            dashboard_data, monthly_volume_data = preprocess_data(data_list)
            # Kafka에 데이터 전송
            producer.send_to_kafka('dashboard_status', dashboard_data)
            producer.send_to_kafka('monthly_volume_status', monthly_volume_data)
        producer.flush()
        print("[성공] Producer 작업 완료")
    except Exception as e:
        print(f"[오류] Producer 작업 중 오류 발생: {e}")

if __name__ == "__main__":
    try:
        # Producer 작업 실행
        print("[정보] Producer 작업을 시작합니다.")
        producer_task()

        # PySpark Consumer 실행 (별도 스레드)
        print("[정보] PySpark Consumer 작업을 시작합니다.")
        consumer_thread = threading.Thread(target=start_spark_consumer)
        consumer_thread.start()

        # 스레드가 완료될 때까지 기다림
        consumer_thread.join()
        print("[성공] PySpark Consumer 작업 완료")
    except Exception as e:
        print(f"[오류] 메인 실행 중 오류 발생: {e}")
