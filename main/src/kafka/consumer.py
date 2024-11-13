# src/kafka/consumer.py
from confluent_kafka import Consumer, KafkaError
import logging
from queue import Queue
import json
import pandas as pd
from src.config.config_manager import ConfigManager

config = ConfigManager()
data_queue = Queue()  # 전역 대기열

class KafkaConsumerService:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': config.kafka.BOOTSTRAP_SERVERS,
            'group.id': 'dashboard-consumer-group',
            'auto.offset.reset': 'latest'
        })
        self.consumer.subscribe([config.kafka.TOPICS['dashboard_status']])
        self.logger = logging.getLogger(__name__)

    def consume_messages(self):
        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                self.logger.error(f"Kafka Consumer 오류: {msg.error()}")
                continue
            message = msg.value().decode('utf-8')
            data_queue.put(message)  # 대기열에 추가하여 Dash에서 사용
