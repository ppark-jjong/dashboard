from kafka import KafkaProducer
import json
import time

# Kafka Producer 생성
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 간단한 데이터 예시
data = {'id': 1, 'name': 'John Doe', 'age': 29}

# 데이터 전송
for i in range(10):
    data['id'] = i
    producer.send('test_topic', value=data)
    print(f"Produced: {data}")
    time.sleep(1)  # 1초 간격으로 전송

producer.flush()
producer.close()
