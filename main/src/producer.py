import time
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
import os

class KafkaProducer:
    def __init__(self):
        # Kafka 브로커 설정
        self.bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topics = {
            'dashboard_status': 'dashboard_status',
            'monthly_volume_status': 'monthly_volume_status'
        }
        conf = {'bootstrap.servers': self.bootstrap_servers}
        self.producer = Producer(conf)
        self.create_or_update_topics()

    def create_or_update_topics(self):
        try:
            admin_client = AdminClient({'bootstrap.servers': self.bootstrap_servers})
            existing_topics = admin_client.list_topics().topics.keys()

            topics_to_create = []
            topics_to_delete = []

            for topic in self.topics.values():
                if topic in existing_topics:
                    # 기존 토픽 삭제 요청
                    print(f"[정보] 기존 토픽 '{topic}' 삭제 요청 중...")
                    topics_to_delete.append(topic)

            if topics_to_delete:
                # 토픽 삭제 요청
                fs = admin_client.delete_topics(topics_to_delete, operation_timeout=30)
                for topic, f in fs.items():
                    try:
                        f.result()  # The result itself is None
                        print(f"[정보] 기존 토픽 '{topic}' 삭제 성공")
                    except Exception as e:
                        print(f"[오류] 기존 토픽 '{topic}' 삭제 실패: {e}")

                # 토픽이 완전히 삭제되었는지 확인하기 위해 대기
                time.sleep(10)  # 10초 대기 (필요에 따라 조정 가능)

            # 새로운 토픽 생성
            for topic in self.topics.values():
                topics_to_create.append(NewTopic(topic=topic, num_partitions=1, replication_factor=1))

            if topics_to_create:
                fs = admin_client.create_topics(topics_to_create)
                for topic, f in fs.items():
                    try:
                        f.result()  # The result itself is None
                        print(f"[정보] 새로운 토픽 '{topic}' 생성 성공")
                    except Exception as e:
                        print(f"[오류] 새로운 토픽 '{topic}' 생성 실패: {e}")

        except Exception as e:
            print(f"[오류] 토픽 생성 또는 업데이트 절차 중 오류 발생: {e}")

    def delivery_report(self, err, msg):
        """메시지 전송 후 콜백 함수"""
        if err is not None:
            print(f"[오류] 메시지 전송 실패: {err}")
        else:
            print(f"[성공] 메시지 전송 성공: {msg.topic()}")

    def send_to_kafka(self, topic, message):
        try:
            self.producer.produce(topic, value=message.SerializeToString(), callback=self.delivery_report)
            self.producer.poll(1)
            print(f"[성공] {topic} 토픽으로 데이터 전송 성공")
        except Exception as e:
            print(f"[오류] Kafka로 {topic} 데이터 전송 중 오류 발생: {e}")

    def flush(self):
        """프로듀서 버퍼 비우기"""
        try:
            self.producer.flush()
        except Exception as e:
            print(f"[오류] 프로듀서 플러시 중 오류 발생: {e}")
