from confluent_kafka import Producer
from protos import delivery_status_pb2
import os


# Kafka 프로듀서를 초기화하는 클래스
class KafkaProducer:
    def __init__(self):
        # Kafka Producer 설정
        conf = {
            'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        }
        self.producer = Producer(conf)

    # 메시지 전송 완료 여부를 확인하는 콜백 함수
    def delivery_report(self, err, msg):
        if err is not None:
            print(f"메시지 전송 실패: {err}")
        else:
            print(f"메시지 전송 성공: {msg.key()}")

    def send_to_kafka(self, data):
        try:
            # Proto 메시지 생성
            delivery_status = delivery_status_pb2.DeliveryStatus()
            delivery_status.order_id = data[0]
            delivery_status.order_date = data[1]
            delivery_status.ship_to = data[2]
            delivery_status.eta = data[3]
            delivery_status.sla = data[4]
            delivery_status.carrier = data[5]
            delivery_status.tracking_number = data[6]
            delivery_status.status = data[7]
            delivery_status.dps = data[8]
            delivery_status.ship_date = data[9]
            delivery_status.delivery_date = data[10]
            delivery_status.recipient = data[11]
            delivery_status.customer_reference = data[12]
            delivery_status.address = data[13]
            delivery_status.comments = data[14]

            # Proto 메시지를 직렬화
            proto_message = delivery_status.SerializeToString()

            # Kafka로 메시지 전송
            self.producer.produce(
                os.environ.get('KAFKA_TOPIC', 'delivery_status'),
                value=proto_message,
                callback=self.delivery_report
            )
            # 프로듀서 큐 비우기
            self.producer.poll(0)
        except Exception as e:
            print(f"Kafka로 데이터 전송 중 오류 발생: {e}")
