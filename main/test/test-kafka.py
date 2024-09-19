from kafka import KafkaProducer
import time

# Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    value_serializer=lambda v: str(v).encode('utf-8')
)

# 메시지 전송
for i in range(10):
    message = f"Message {i}"
    producer.send('test_topic', value=message)
    print(f"Produced: {message}")
    time.sleep(1)

producer.flush()
producer.close()
