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
            delivery_status.delivery_agent = data[0]  # 배송 기사
            delivery_status.order_date = data[1]  # Date(접수일)
            delivery_status.dps = data[2]  # DPS#
            delivery_status.eta = data[3]  # ETA
            delivery_status.sla = data[4]  # SLA
            delivery_status.address = data[5]  # Ship to
            delivery_status.status_detail = data[6]  # Status
            delivery_status.picked = data[7].strip().upper() == "O"  # 1. Picked
            delivery_status.shipped = data[8].strip().upper() == "O"  # 2. Shipped
            delivery_status.pod = data[9].strip().upper() == "O"  # 3. POD
            delivery_status.zip_code = int(data[10])  # Zip Code
            delivery_status.distance = int(data[11])  # Billed Distance (Put into system)
            delivery_status.recipient = data[12]  # 인수자
            delivery_status.issue = data[13].strip().upper() == "O"  # issue

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
