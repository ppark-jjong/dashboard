from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

# Kafka 설정
KAFKA_BROKER = 'kafka:9092'  # Docker 환경에서 Kafka의 주소를 올바르게 설정
KAFKA_TOPIC = 'delivery-data'

# Spark 세션 생성
try:
    spark = SparkSession.builder \
        .appName("DeliveryStatusConsumer") \
        .master("spark://spark-master:7077") \
        .getOrCreate()
    print("[Consumer] Spark 세션이 생성되었습니다.")
except Exception as e:
    print(f"[Consumer] Spark 세션 생성 중 오류 발생: {e}")

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

print("[Consumer] Kafka에서 들어오는 데이터의 스키마가 정의되었습니다.")

# Kafka에서 데이터를 읽어오는 스트리밍 데이터프레임 생성
try:
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()
    print("[Consumer] Kafka에서 데이터를 읽어오는 중...")
except Exception as e:
    print(f"[Consumer] Kafka에서 데이터 읽기 중 오류 발생: {e}")

# 데이터 변환 및 전처리
try:
    value_df = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*") \
        .withColumn("date", to_date(col("date"), "yyyy-MM-dd"))

    print("[Consumer] Kafka에서 받은 원본 데이터 스키마:")
    value_df.printSchema()  # 데이터의 스키마를 출력하여 확인
except Exception as e:
    print(f"[Consumer] 데이터 전처리 중 오류 발생: {e}")

# 콘솔로 처리된 데이터를 출력하는 스트리밍 설정
def process_row(batch_df, batch_id):
    print(f"[Consumer] Batch ID: {batch_id} 처리 중...")  # 배치 ID 출력
    print("[Consumer] 현재 배치에서 수신된 데이터:")
    batch_df.show(truncate=False)  # 실제 데이터를 콘솔에 출력하여 확인

# 스트리밍 쿼리를 정의하여 데이터 처리
try:
    query = value_df.writeStream \
        .foreachBatch(process_row) \
        .outputMode("append") \
        .start()
    print("[Consumer] Spark 스트리밍 쿼리가 시작되었습니다.")
except Exception as e:
    print(f"[Consumer] 스트리밍 쿼리 실행 중 오류 발생: {e}")

# 스트리밍이 종료되지 않도록 대기
try:
    query.awaitTermination()
except Exception as e:
    print(f"[Consumer] 스트리밍 종료 대기 중 오류 발생: {e}")
