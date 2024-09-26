from confluent_kafka import Producer
from protos import delivery_status_pb2
import os

class KafkaProducer:
    def __init__(self):
        conf = {
            'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        }
        self.producer = Producer(conf)

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"메시지 전송 실패: {err}")
        else:
            print(f"메시지 전송 성공: {msg.topic()} [{msg.partition()}]")

    def send_to_kafka(self, data):
        try:
            delivery_status = delivery_status_pb2.DeliveryStatus()
            delivery_status.delivery_agent = data[0]
            delivery_status.order_date = data[1]
            delivery_status.dps = data[2]
            delivery_status.eta = data[3]
            delivery_status.sla = data[4]
            delivery_status.address = data[5]
            delivery_status.status_detail = data[6]
            delivery_status.picked = data[7].strip().upper() == "O"
            delivery_status.shipped = data[8].strip().upper() == "O"
            delivery_status.pod = data[9].strip().upper() == "O"
            delivery_status.zip_code = int(data[10])
            delivery_status.distance = int(data[11])
            delivery_status.recipient = data[12]
            delivery_status.issue = data[13].strip().upper() == "O"

            proto_message = delivery_status.SerializeToString()
            self.producer.produce(
                os.environ.get('KAFKA_TOPIC', 'delivery_status'),
                key=str(delivery_status.dps),
                value=proto_message,
                callback=self.delivery_report
            )
            self.producer.poll(1)
        except Exception as e:
            print(f"Kafka로 데이터 전송 중 오류 발생: {e}")

    def flush(self):
        self.producer.flush()
