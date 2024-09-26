import time
from googleApi import get_sheet_data, preprocess_data
from producer import KafkaProducer
import threading
from consumer import start_consumer
import os
os.environ['KAFKA_BOOTSTRAP_SERVERS'] = 'localhost:9092'

# Producer 작업을 수행하는 함수
def producer_task():
    producer = KafkaProducer()
    invalid_data_flag = False  # 오류 메시지 출력 여부 플래그

    while True:
        # Google Sheets에서 데이터를 가져옴
        data_list = get_sheet_data()
        if data_list:
            # 데이터 전처리
            processed_data = preprocess_data(data_list)

            for _, data in processed_data.iterrows():
                try:
                    if len(data) == 14:
                        producer.send_to_kafka(data.tolist())
                        print("[성공] 데이터 전송 성공")
                    else:
                        if not invalid_data_flag:
                            print(f"[오류] 데이터 형식이 올바르지 않습니다. 필드 수: {len(data)}")
                            invalid_data_flag = True
                except Exception as e:
                    print(f"[오류] 데이터 전송 중 오류 발생: {e}")
        else:
            print("[오류] Google Sheets에서 데이터를 가져오지 못했습니다.")

        # 10초마다 데이터를 가져옴
        time.sleep(10)

    # 프로듀서 버퍼 비우기
    producer.flush()

if __name__ == "__main__":
    # 컨슈머를 별도의 스레드로 실행
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.start()

    # 프로듀서 작업 실행
    producer_task()
