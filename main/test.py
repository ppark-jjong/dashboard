from confluent_kafka import Producer

# Producer 설정
producer = Producer({'bootstrap.servers': 'localhost:9092'})

# 메시지 전송 콜백 함수
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# 테스트 데이터 전송
data_list = [
    {'sensor_id': 'sensor_1', 'value': 30.5},
    {'sensor_id': 'sensor_2', 'value': 22.1},
    {'sensor_id': 'sensor_3', 'value': 45.3},
]

for data in data_list:
    producer.produce('test-topic', value=str(data), callback=delivery_report)
    producer.poll(0)

producer.flush()
