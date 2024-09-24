import time
from producer import Producer
from google
import threading
from consumer import start_spark_streaming


def producer_task():
    """Producer 작업을 수행하는 함수"""
    producer = Producer()
    while True:
        # Google Sheets에서 데이터를 가져옴
        data_list = get_sheet_data()
        if data_list:
            for data in data_list:
                if len(data) == 5:
                    # 데이터 전송
                    producer.send_to_kafka(data)
                else:
                    print("데이터 형식이 올바르지 않습니다.")
        else:
            print("Google Sheets에서 데이터를 가져오지 못했습니다.")

        # 10초마다 데이터를 가져옴
        time.sleep(10)


if __name__ == "__main__":
    # 컨슈머를 별도의 스레드로 실행
    consumer_thread = threading.Thread(target=start_spark_streaming)
    consumer_thread.start()

    # 프로듀서 작업 실행
    producer_task()
