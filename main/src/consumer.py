
import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경 변수에서 설정 가져오기
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = 'delivery-data'
SPARK_MASTER = os.getenv('SPARK_MASTER', 'local[*]')

def create_spark_session():
    logger.info("Consumer: Spark 세션 생성 중...")
    return SparkSession.builder \
        .appName("DeliveryStatusConsumer") \
        .master(SPARK_MASTER) \
        .getOrCreate()

def create_streaming_df(spark):
    logger.info("Consumer: Kafka 스트리밍 데이터프레임 생성 중...")
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

def process_row(batch_df, batch_id):
    logger.info(f"Consumer: Batch ID {batch_id} 처리 중...")
    logger.info("Consumer: 현재 배치에서 수신된 데이터:")
    batch_df.show(truncate=False)

def start_consumer():
    spark = create_spark_session()
    df = create_streaming_df(spark)

    # Kafka에서 들어오는 데이터의 스키마 정의
    schema = StructType([
        StructField("type", StringType(), True),
        StructField("date", StringType(), True),
        StructField("status_counts", StringType(), True),
        StructField("completion_rate", FloatType(), True),
        StructField("avg_distance", FloatType(), True),
        StructField("issue_count", IntegerType(), True),
        StructField("week", StringType(), True),
        StructField("issue_pattern", StringType(), True)
    ])

    logger.info("Consumer: 데이터 스키마 정의 완료")

    # 데이터 변환 및 전처리
    try:
        value_df = df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*") \
            .withColumn("date", to_date(col("date"), "yyyy-MM-dd"))

        logger.info("Consumer: 데이터 전처리 완료")
    except Exception as e:
        logger.error(f"Consumer: 데이터 전처리 중 오류 발생 - {e}")
        return

    # 스트리밍 쿼리 정의 및 실행
    try:
        query = value_df.writeStream \
            .foreachBatch(process_row) \
            .outputMode("append") \
            .start()

        logger.info("Consumer: Spark 스트리밍 쿼리 시작")
        query.awaitTermination()
    except Exception as e:
        logger.error(f"Consumer: 스트리밍 쿼리 실행 중 오류 발생 - {e}")
    finally:
        logger.info("Consumer: Spark 세션 종료")
        spark.stop()

if __name__ == "__main__":
    logger.info("Consumer: 독립 실행 모드로 시작")
    start_consumer()
