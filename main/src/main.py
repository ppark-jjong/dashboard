from producer import create_producer
import time

# 메인 실행 함수
def main(interval=300):
    producer = create_producer()
    try:
        while True:
            try:
                producer.process_and_send_data()  # 메서드 이름 수정
                time.sleep(interval)
            except Exception as e:
                print(f"오류가 발생했습니다: {e}")
                time.sleep(60)  # 오류 발생 시 1분 후 재시도
    finally:
        producer.close()

if __name__ == "__main__":
    print("Google Sheets 배송 데이터 분석 및 전송을 시작합니다...")
    main()