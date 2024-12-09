from pyspark.sql import SparkSession
from src.config import main_config as config

def create_spark_session():
    """
    PySpark 세션 생성
    """
    return (
        SparkSession.builder
        .appName(config.SPARK_APP_NAME)
        .master(config.SPARK_MASTER_URL)
        .config("spark.executor.memory", "2g")
        .getOrCreate()
    )
