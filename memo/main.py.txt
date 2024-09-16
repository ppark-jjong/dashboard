from producer import create_producer
import time

# Producer 실행 함수
def start_producer(interval=300):
    # DeliveryProducer 객체 생성
    producer = create_producer()
    try:
        while True:
            try:
                print("데이터 수집 및 Kafka 전송 작업을 시작합니다...")
                producer.process_and_send_data()  # Google Sheets 데이터 처리 및 전송
                print("데이터 수집 및 전송 작업이 완료되었습니다.")
                time.sleep(interval)  # 지정된 간격(초)마다 실행
            except Exception as e:
                print(f"오류가 발생했습니다: {e}")
                time.sleep(60)  # 오류 발생 시 1분 후 재시도
    finally:
        print("프로듀서 연결을 종료합니다.")
        producer.close()  # 프로듀서 연결 종료

if __name__ == "__main__":
    print("Google Sheets 배송 데이터 분석 및 전송을 시작합니다...")
    start_producer()
