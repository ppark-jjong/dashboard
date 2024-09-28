from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, MapType
import os

# Kafka에서 데이터를 읽어오는 스키마 정의
dashboard_schema = StructType([
    StructField("picked_count", IntegerType(), True),
    StructField("shipped_count", IntegerType(), True),
    StructField("pod_count", IntegerType(), True),
    StructField("sla_counts_today", MapType(StringType(), IntegerType()), True),
    StructField("issues_today", StringType(), True)
])

monthly_volume_schema = StructType([
    StructField("sla_counts_month", MapType(StringType(), IntegerType()), True),
    StructField("weekday_counts", MapType(StringType(), IntegerType()), True),
    StructField("distance_counts", MapType(IntegerType(), IntegerType()), True)
])
#    PySpark를 이용해 Kafka 토픽에서 메시지 소비 및 처리
def start_spark_consumer():
    try:
        # SparkSession 초기화
        spark = SparkSession.builder.appName("KafkaProtoBufConsumer").getOrCreate()

        print("[정보] PySpark가 Kafka 토픽에서 데이터를 소비 중...")

        # dashboard_status 토픽 데이터 스트림 읽기
        df_dashboard = spark.readStream.format("kafka")\
            .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'))\
            .option("subscribe", "dashboard_status")\
            .option("startingOffsets", "earliest")\
            .load()

        # JSON으로 변환 및 콘솔 출력
        df_dashboard = df_dashboard.withColumn("value", from_json(df_dashboard["value"].cast("string"), dashboard_schema))
        query_dashboard = df_dashboard.selectExpr("value.*")\
            .writeStream\
            .outputMode("append")\
            .format("console")\
            .start()

        # monthly_volume_status 토픽 데이터 스트림 읽기
        df_monthly_volume = spark.readStream.format("kafka")\
            .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'))\
            .option("subscribe", "monthly_volume_status")\
            .option("startingOffsets", "earliest")\
            .load()

        # JSON으로 변환 및 콘솔 출력
        df_monthly_volume = df_monthly_volume.withColumn("value", from_json(df_monthly_volume["value"].cast("string"), monthly_volume_schema))
        query_monthly_volume = df_monthly_volume.selectExpr("value.*")\
            .writeStream\
            .outputMode("append")\
            .format("console")\
            .start()

        print("[성공] PySpark가 Kafka로부터 데이터를 소비하고 있습니다.")

        # 스트림 종료 대기
        query_dashboard.awaitTermination()
        query_monthly_volume.awaitTermination()
    except Exception as e:
        print(f"[오류] PySpark Consumer 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    start_spark_consumer()
