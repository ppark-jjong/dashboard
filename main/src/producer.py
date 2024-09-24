
from kafka import KafkaProducer
import delivery_status_pb2  # 컴파일된 Proto 파일 import

# Kafka 설정
KAFKA_TOPIC = 'delivery_status'
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']  # Kafka 브로커 주소 설정

class Producer:
    def __init__(self):
        # Kafka Producer 설정 (바이트 배열 전송을 위해 설정)
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    def send_to_kafka(self, data):
        """Kafka에 Proto 메시지를 전송하는 함수"""
        try:
            # Proto 메시지 생성
            delivery_status = delivery_status_pb2.DeliveryStatus()
            delivery_status.order_id = data[0]
            delivery_status.customer_name = data[1]
            delivery_status.delivery_address = data[2]
            delivery_status.status = data[3]
            delivery_status.timestamp = data[4]

            # Proto 메시지를 직렬화
            proto_message = delivery_status.SerializeToString()

            # Kafka로 메시지 전송
            self.producer.send(KAFKA_TOPIC, proto_message)
            print("데이터 전송 성공")
        except Exception as e:
            print(f"Kafka로 데이터 전송 중 오류 발생: {e}")
