# 간단한 Kafka Producer 예제
from kafka import KafkaProducer

# Kafka Producer 설정
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# 메시지 전송 테스트
producer.send('test_topic', b'Test message')
producer.flush()
producer.close()
print("Kafka 연결 테스트 완료")
