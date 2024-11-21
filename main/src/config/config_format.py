from confluent_kafka import Producer
from pyspark.sql import SparkSession
from src.config.logger import Logger

logger = Logger.get_logger(__name__)


# Dashboard 관련 데이터 컬럼
class DashBoardConfig:
    DASHBOARD_COLUMNS = [
        'Delivery', 'DPS', 'ETA', 'SLA', 'Address',
        'Status', 'Recipient'
    ]


# Kafka 설정 정보
class KafkaConfig:
    BOOTSTRAP_SERVERS = 'localhost:9092'
    RAW_TOPIC = 'raw_deliveries'
    TOPICS = {
        'regional_trends': 'regional_trends',
        'time_based_trends': 'time_based_trends',
        'delivery_performance': 'delivery_performance',
        'driver_delivery_trends': 'driver_delivery_trends'
    }

    @staticmethod
    def get_producer():
        return Producer({'bootstrap.servers': KafkaConfig.BOOTSTRAP_SERVERS})


# Spark 설정 정보 (싱글톤)
class SparkConfig:
    """
    싱글톤 패턴으로 SparkSession을 관리하는 클래스.
    """
    _spark_instance = None  # SparkSession을 저장할 클래스 변수

    @staticmethod
    def get_instance(app_name: str = "DeliveryAnalytics", master: str = "local[*]", executor_memory: str = "2g"):
        """
        SparkSession 인스턴스를 반환합니다. 없으면 새로 생성합니다.
        """
        if SparkConfig._spark_instance is None:
            logger.info("Initializing SparkSession...")
            SparkConfig._spark_instance = SparkSession.builder \
                .appName(app_name) \
                .master(master) \
                .config("spark.executor.memory", executor_memory) \
                .getOrCreate()
            logger.info("SparkSession initialized.")
        return SparkConfig._spark_instance

    @staticmethod
    def stop_instance():
        """
        SparkSession을 종료합니다.
        """
        if SparkConfig._spark_instance is not None:
            logger.info("Stopping SparkSession...")
            SparkConfig._spark_instance.stop()
            SparkConfig._spark_instance = None
            logger.info("SparkSession stopped.")
