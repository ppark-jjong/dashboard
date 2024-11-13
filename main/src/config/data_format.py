# Kafka, Spark 설정

from confluent_kafka import Producer
# from pyspark.sql import SparkSession

class DashBoardConfig:
    DASHBOARD_COLUMNS = [
        'Delivery', 'DPS', 'ETA', 'SLA', 'Address',
        'Status', 'Billed Distance', 'Recipient'
    ]

class KafkaConfig:
    BOOTSTRAP_SERVERS = 'localhost:9092'
    TOPICS = {
        'realtime_status': 'realtime_status',
        'weekly_analysis': 'weekly_analysis',
        'monthly_analysis': 'monthly_analysis',
        'dashboard_status': 'dashboard_status',
        'monthly_volume_status': 'monthly_volume_status'
    }

    @staticmethod
    def get_producer():
        return Producer({'bootstrap.servers': KafkaConfig.BOOTSTRAP_SERVERS})

# class SparkConfig:
#     APP_NAME = "DeliveryAnalytics"
#     MASTER = "spark://spark-master:7077"
#     EXECUTOR_MEMORY = "2g"
#
#     @staticmethod
#     def get_spark_session():
#         return SparkSession.builder \
#             .appName(SparkConfig.APP_NAME) \
#             .master(SparkConfig.MASTER) \
#             .config("spark.executor.memory", SparkConfig.EXECUTOR_MEMORY) \
#             .getOrCreate()
