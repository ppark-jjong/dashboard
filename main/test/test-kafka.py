from confluent_kafka import Producer, Consumer, KafkaError
import time


# Kafka Producer 설정
def produce_message():
    producer = Producer({'bootstrap.servers': 'kafka:9092'})
    for i in range(10):
        producer.produce('test_topic', f'Message {i}')
        producer.flush()
        time.sleep(1)
    print("메시지 전송 완료")


# Kafka Consumer 설정
def consume_message():
    consumer = Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'test_group',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe(['test_topic'])

    print("메시지 소비 시작...")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break
        print(f'Consumed message: {msg.value().decode("utf-8")}')

    consumer.close()


if __name__ == "__main__":
    produce_message()  # 메시지 전송
    consume_message()  # 메시지 소비
