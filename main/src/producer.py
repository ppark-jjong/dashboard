from confluent_kafka import Producer
import os

# Kafka 프로듀서를 초기화하는 클래스
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
