import threading
from producer import KafkaProducer
from googleApi import get_sheet_data, preprocess_data
from src.consumer import start_spark_consumer


def producer_task():
    try:
        producer = KafkaProducer()
        data_list = get_sheet_data()
        if data_list:
            dashboard_data, monthly_volume_data = preprocess_data(data_list)
            producer.send_to_kafka('dashboard_status', dashboard_data)
            producer.send_to_kafka('monthly_volume_status', monthly_volume_data)
        producer.flush()
    except Exception as e:
        print(f"[오류] Producer 작업 중 오류 발생: {e}")

if __name__ == "__main__":
    try:
        # Producer 작업 실행
        producer_task()

        # PySpark Consumer 실행
        consumer_thread = threading.Thread(target=start_spark_consumer)
        consumer_thread.daemon = True
        consumer_thread.start()

    except Exception as e:
        print(f"[오류] 메인 실행 중 오류 발생: {e}")
