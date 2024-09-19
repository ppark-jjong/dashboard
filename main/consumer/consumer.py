import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경 변수에서 설정 가져오기
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = 'delivery-data'
SPARK_MASTER = os.getenv('SPARK_MASTER', 'local[*]')

# Spark 세션 생성 함수
def create_spark_session():
    logger.info("🛠Spark 세션을 생성 중입니다...")
    return SparkSession.builder \
        .appName("DeliveryStatusConsumer") \
        .master(SPARK_MASTER) \
        .getOrCreate()

# Kafka 스트리밍 데이터프레임 생성 함수
def create_streaming_df(spark):
    logger.info("Kafka 스트리밍 데이터프레임을 생성 중입니다...")
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

# 각 배치 데이터 처리 함수
def process_row(batch_df, batch_id):
    logger.info(f"Batch ID {batch_id} 처리 중...")
    batch_df.show(truncate=False)

# Consumer 실행 함수
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

    logger.info("데이터 스키마 정의 완료.")

    # 데이터 변환 및 전처리
    try:
        value_df = df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*") \
            .withColumn("date", to_date(col("date"), "yyyy-MM-dd"))
        logger.info("데이터 전처리 완료.")
    except Exception as e:
        logger.error(f"데이터 전처리 중 오류 발생: {e}")
        return

    # 스트리밍 쿼리 정의 및 실행
    try:
        query = value_df.writeStream \
            .foreachBatch(process_row) \
            .outputMode("append") \
            .start()
        logger.info(" Spark 스트리밍 쿼리를 시작합니다.")
        query.awaitTermination()
    except Exception as e:
        logger.error(f"스트리밍 쿼리 실행 중 오류 발생: {e}")
    finally:
        logger.info("Spark 세션을 종료합니다.")
        spark.stop()

# 독립 실행 시 호출되는 메인 함수
if __name__ == "__main__":
    logger.info("Consumer: 독립 실행 모드로 시작합니다.")
    start_consumer()
