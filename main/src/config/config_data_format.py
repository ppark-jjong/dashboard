from confluent_kafka import Producer
from pyspark.sql import SparkSession

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

# Spark 설정 정보
class SparkConfig:
    APP_NAME = "DeliveryAnalytics"
    MASTER = "spark://spark-master:7077"
    EXECUTOR_MEMORY = "2g"

    @staticmethod
    def get_spark_session():
        return SparkSession.builder \
            .appName(SparkConfig.APP_NAME) \
            .master(SparkConfig.MASTER) \
            .config("spark.executor.memory", SparkConfig.EXECUTOR_MEMORY) \
            .getOrCreate()

