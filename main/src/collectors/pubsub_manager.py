from google.cloud import pubsub_v1
from src.config.gcp_config import GCPConfig
from src.config.logger import Logger
import json

logger = Logger.get_logger(__name__)

class PubSubManager:
    def __init__(self):
        # Pub/Sub 클라이언트 초기화
        self.publisher = GCPConfig.get_pubsub_publisher()
        self.subscriber = GCPConfig.get_pubsub_subscriber()
        self.topic_path = self.publisher.topic_path(GCPConfig.PROJECT_ID, GCPConfig.TOPIC_NAME)
        self.subscription_path = self.subscriber.subscription_path(GCPConfig.PROJECT_ID, GCPConfig.SUBSCRIPTION_NAME)

    def publish(self, data: dict) -> str:
        """
        Pub/Sub 메시지 발행
        """
        try:
            message = json.dumps(data).encode("utf-8")
            future = self.publisher.publish(self.topic_path, message)
            message_id = future.result()
            logger.info(f"Published message with ID: {message_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise RuntimeError("Pub/Sub publish failed")

    def consume(self) -> list:
        """
        Pub/Sub 메시지 소비
        """
        consumed_messages = []

        def callback(message):
            logger.info(f"Received message: {message.data.decode('utf-8')}")
            consumed_messages.append(json.loads(message.data))
            message.ack()

        try:
            streaming_pull_future = self.subscriber.subscribe(self.subscription_path, callback=callback)
            logger.info(f"Listening for messages on {self.subscription_path}")
            streaming_pull_future.result(timeout=5)  # 메시지 소비 대기 시간 설정
        except Exception as e:
            logger.error(f"Failed to consume messages: {e}")
            raise RuntimeError("Pub/Sub consume failed")

        return consumed_messages
