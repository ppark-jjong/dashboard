import time
from confluent_kafka.admin import NewTopic
from config_manager import ConfigManager

class KafkaProducer:
    def __init__(self):
        self.config = ConfigManager()
        self.producer = self.config.get_kafka_producer()
        self.topics = self.config.KAFKA_TOPICS
        self.create_or_update_topics()

    def create_or_update_topics(self):
        try:
            admin_client = self.config.get_kafka_admin_client()
            existing_topics = admin_client.list_topics().topics.keys()

            topics_to_create = []
            topics_to_delete = []

            for topic in self.topics.values():
                if topic in existing_topics:
                    print(f"[정보] 기존 토픽 '{topic}' 삭제 요청 중...")
                    topics_to_delete.append(topic)

            if topics_to_delete:
                fs = admin_client.delete_topics(topics_to_delete, operation_timeout=30)
                for topic, f in fs.items():
                    try:
                        f.result()
                        print(f"[정보] 기존 토픽 '{topic}' 삭제 성공")
                    except Exception as e:
                        print(f"[오류] 기존 토픽 '{topic}' 삭제 실패: {e}")

                time.sleep(10)

            for topic in self.topics.values():
                topics_to_create.append(NewTopic(topic=topic, num_partitions=1, replication_factor=1))

            if topics_to_create:
                fs = admin_client.create_topics(topics_to_create)
                for topic, f in fs.items():
                    try:
                        f.result()
                        print(f"[정보] 새로운 토픽 '{topic}' 생성 성공")
                    except Exception as e:
                        print(f"[오류] 새로운 토픽 '{topic}' 생성 실패: {e}")

        except Exception as e:
            print(f"[오류] 토픽 생성 또는 업데이트 절차 중 오류 발생: {e}")

    def delivery_report(self, err, msg):
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
        try:
            self.producer.flush()
        except Exception as e:
            print(f"[오류] 프로듀서 플러시 중 오류 발생: {e}")