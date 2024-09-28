from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, MapType
import os
import pandas as pd

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

def save_to_excel(pandas_df, file_name):
    try:
        absolute_path = "C:\\MyMain\\dashboard\\main\\xlsx"  # 절대경로 설정

        # 디렉토리가 존재하는지 확인하고 없으면 생성
        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)
            print(f"[정보] 디렉토리가 생성되었습니다: {absolute_path}")

        file_path = os.path.join(absolute_path, file_name)
        pandas_df.to_excel(file_path, index=False)
        print(f"[성공] 엑셀 파일로 저장 완료: {file_path}")
    except Exception as e:
        print(f"[오류] 엑셀 파일로 저장 중 오류 발생: {e}")

def process_batch(df, epoch_id, schema, file_name):
    try:
        print(f"[정보] {file_name} 배치를 처리 중...")
        if df.count() == 0:
            print(f"[경고] {file_name} 배치에서 데이터가 없음.")
            return
        df = df.selectExpr("value.*")
        pandas_df = df.toPandas()
        save_to_excel(pandas_df, file_name)
    except Exception as e:
        print(f"[오류] 배치 처리 중 오류 발생: {e}")
from pyspark.sql import SparkSession
import os

def start_spark_consumer():
    try:
        # JAR 파일 경로 지정
        jars_path = os.path.join("C:", "MyMain", "dashboard", "main", "jars",
                                 "spark-sql-kafka-0-10_2.12-3.5.2.jar,"
                                 "kafka-clients-3.5.0.jar")

        # SparkSession 초기화 (JAR 파일 경로 추가)
        spark = SparkSession.builder \
            .appName("KafkaProtoBufConsumer") \
            .config("spark.jars", jars_path) \
            .getOrCreate()

        print("[정보] PySpark가 Kafka 토픽에서 데이터를 소비 중...")

        # Kafka에서 데이터 읽기
        df_dashboard = spark.readStream.format("kafka") \
            .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')) \
            .option("subscribe", "dashboard_status") \
            .option("startingOffsets", "earliest") \
            .load()

        df_dashboard = df_dashboard.withColumn("value", from_json(df_dashboard["value"].cast("string"), dashboard_schema))

        # monthly_volume_status 토픽 데이터 스트림 읽기
        df_monthly_volume = spark.readStream.format("kafka") \
            .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')) \
            .option("subscribe", "monthly_volume_status") \
            .option("startingOffsets", "earliest") \
            .load()

        df_monthly_volume = df_monthly_volume.withColumn("value", from_json(df_monthly_volume["value"].cast("string"),
                                                                            monthly_volume_schema))

        # 각 배치를 처리하여 엑셀로 저장
        query_dashboard = df_dashboard.writeStream \
            .foreachBatch(lambda df, epoch_id: process_batch(df, epoch_id, dashboard_schema, "dashboard_status.xlsx")) \
            .start()

        query_monthly_volume = df_monthly_volume.writeStream \
            .foreachBatch(lambda df, epoch_id: process_batch(df, epoch_id, monthly_volume_schema, "monthly_volume_status.xlsx")) \
            .start()

        print("[성공] PySpark가 Kafka로부터 데이터를 소비하고 엑셀로 저장합니다.")

        # 스트림 종료 대기
        query_dashboard.awaitTermination()
        query_monthly_volume.awaitTermination()

    except Exception as e:
        print(f"[오류] PySpark Consumer 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    start_spark_consumer()
