from confluent_kafka import Producer
import os

<<<<<<< HEAD
=======
# Kafka 프로듀서를 초기화하는 클래스
>>>>>>> origin/main
class KafkaProducer:
    def __init__(self):
        conf = {
            'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        }
        self.producer = Producer(conf)

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"[오류] 메시지 전송 실패: {err}")
        else:
<<<<<<< HEAD
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
=======
            print(f"[성공] 메시지 전송 성공: {msg.key()}")

    def send_dashboard_data_to_kafka(self, data):
        try:
            dashboard_status = dashboard_status_pb2.DashboardStatus()
            dashboard_status.picked_count = data['picked_count']
            dashboard_status.shipped_count = data['shipped_count']
            dashboard_status.pod_count = data['pod_count']
            dashboard_status.sla_counts.update(data['sla_counts_today'])
            dashboard_status.issues.extend(data['issues_today'])

            proto_message = dashboard_status.SerializeToString()
            self.producer.produce(
                os.environ.get('KAFKA_TOPIC', 'dashboard_status'),
                value=proto_message,
                callback=self.delivery_report
            )
            self.producer.poll(0)
        except Exception as e:
            print(f"[오류] Kafka로 대시보드 데이터 전송 중 오류 발생: {e}")

    def send_monthly_volume_data_to_kafka(self, data):
        try:
            monthly_volume_status = monthly_volume_status_pb2.MonthlyVolumeStatus()
            monthly_volume_status.sla_counts.update(data['sla_counts_month'])
            monthly_volume_status.weekday_counts.update(data['weekday_counts'])
            monthly_volume_status.distance_counts.update(data['distance_counts'])

            proto_message = monthly_volume_status.SerializeToString()
            self.producer.produce(
                os.environ.get('KAFKA_TOPIC', 'monthly_volume_status'),
                value=proto_message,
                callback=self.delivery_report
            )
            self.producer.poll(0)
        except Exception as e:
            print(f"[오류] Kafka로 월간 데이터 전송 중 오류 발생: {e}")
>>>>>>> origin/main
