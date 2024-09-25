from confluent_kafka import Consumer, KafkaException
from protos import delivery_status_pb2
import os


# Kafka에서 데이터를 소비하고 처리하는 함수
def start_consumer():
    KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'delivery_status')
    KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    KAFKA_GROUP_ID = os.environ.get('KAFKA_GROUP_ID', 'delivery_consumer_group')

    # Kafka Consumer 설정
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_GROUP_ID,
        'auto.offset.reset': 'earliest'
    }

    # Kafka Consumer 초기화
    consumer = Consumer(conf)
    consumer.subscribe([KAFKA_TOPIC])

    try:
        while True:
            # 메시지를 소비
            msg = consumer.poll(1.0)  # 1초 대기
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer 오류: {msg.error()}")
                continue

            # 메시지 처리
            try:
                # Proto 메시지 역직렬화
                delivery_status = delivery_status_pb2.DeliveryStatus()
                delivery_status.ParseFromString(msg.value())

                # 결과 출력
                print(f"주문ID: {delivery_status.order_id}, 고객명: {delivery_status.customer_name}, 주소: {delivery_status.delivery_address}, 상태: {delivery_status.status}, 시간: {delivery_status.timestamp}")
            except Exception as e:
                print(f"메시지 처리 중 오류 발생: {e}")
    except KeyboardInterrupt:
        pass
    finally:
        # 종료 시 컨슈머 닫기
        consumer.close()
