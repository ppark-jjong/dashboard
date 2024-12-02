import os
from google.cloud import storage, pubsub_v1
from src.config.logger import Logger

logger = Logger.get_logger(__name__)

class GCPConfig:
    """
    GCP 설정 및 클라이언트 관리
    """
    # 환경 변수 기반 설정
    PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
    BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "your-bucket-name")
    TOPIC_NAME = os.getenv("GCP_TOPIC_NAME", "your-topic-name")
    SUBSCRIPTION_NAME = os.getenv("GCP_SUBSCRIPTION_NAME", "your-subscription-name")
    SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./secrets/google/credentials.json")

    @staticmethod
    def get_pubsub_publisher():
        """
        Pub/Sub Publisher 클라이언트 생성
        """
        try:
            logger.info("Pub/Sub Publisher 클라이언트 초기화 중...")
            return pubsub_v1.PublisherClient()
        except Exception as e:
            logger.error(f"Pub/Sub Publisher 초기화 실패: {e}")
            raise RuntimeError("Pub/Sub Publisher 클라이언트를 초기화할 수 없습니다.")

    @staticmethod
    def get_pubsub_subscriber():
        """
        Pub/Sub Subscriber 클라이언트 생성
        """
        try:
            logger.info("Pub/Sub Subscriber 클라이언트 초기화 중...")
            return pubsub_v1.SubscriberClient()
        except Exception as e:
            logger.error(f"Pub/Sub Subscriber 초기화 실패: {e}")
            raise RuntimeError("Pub/Sub Subscriber 클라이언트를 초기화할 수 없습니다.")

    @staticmethod
    def get_storage_client():
        """
        GCS 클라이언트 생성
        """
        try:
            if not os.path.exists(GCPConfig.SERVICE_ACCOUNT_FILE):
                raise FileNotFoundError(f"GCS 인증 파일이 존재하지 않습니다: {GCPConfig.SERVICE_ACCOUNT_FILE}")
            logger.info("GCS 클라이언트 초기화 중...")
            return storage.Client.from_service_account_json(GCPConfig.SERVICE_ACCOUNT_FILE)
        except Exception as e:
            logger.error(f"GCS 클라이언트 초기화 실패: {e}")
            raise RuntimeError("GCS 클라이언트를 초기화할 수 없습니다.")
