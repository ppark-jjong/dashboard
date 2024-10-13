from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, udf
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, MapType
import os
import pandas as pd
from google.protobuf.json_format import MessageToJson  # Protobuf 메시지를 JSON으로 변환
from proto import dashboard_status_pb2, monthly_volume_status_pb2  # Protobuf 파일 임포트

# Kafka에서 데이터를 읽어오는 스키마 정의 (JSON 데이터용)
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

# Protobuf 역직렬화 함수
def deserialize_proto(proto_bytes, proto_type):
    try:
        proto_obj = proto_type()
        proto_obj.ParseFromString(proto_bytes)
        # Proto 메시지를 JSON으로 변환
        return MessageToJson(proto_obj)
    except Exception as e:
        print(f"[오류] 프로토 역직렬화 중 오류 발생: {e}")
        return None

# UDF 등록 (역직렬화 함수)
deserialize_dashboard_proto_udf = udf(lambda proto_bytes: deserialize_proto(proto_bytes, dashboard_status_pb2.DashboardStatus), StringType())
deserialize_monthly_proto_udf = udf(lambda proto_bytes: deserialize_proto(proto_bytes, monthly_volume_status_pb2.MonthlyVolumeStatus), StringType())

# 엑셀로 저장하는 함수 정의
def save_to_excel(pandas_df, file_name):
    try:
        absolute_path = "C:\\MyMain\\dashboard\\main\\xlsx"  # 절대경로 설정
        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)
            print(f"[정보] 디렉토리가 생성되었습니다: {absolute_path}")

        file_path = os.path.join(absolute_path, file_name)
        pandas_df.to_excel(file_path, index=False)
        print(f"[성공] 엑셀 파일로 저장 완료: {file_path}")
    except Exception as e:
        print(f"[오류] 엑셀 파일로 저장 중 오류 발생: {e}")

# 배치를 처리하는 함수 정의 (foreachBatch에서 호출됨)
def process_batch(df, epoch_id, schema, file_name):
    try:
        print(f"[정보] {file_name} 배치를 처리 중...")

        # 데이터가 없는 경우 처리하지 않음
        if df.count() == 0:
            print(f"[경고] {file_name} 배치에서 데이터가 없음.")
            return

        # 데이터 선택 및 Pandas로 변환
        df = df.selectExpr("value.*")
        pandas_df = df.toPandas()

        # 엑셀 파일로 저장
        save_to_excel(pandas_df, file_name)

    except Exception as e:
        print(f"[오류] 배치 처리 중 오류 발생: {e}")

# 스트림 컨슈머 시작 함수
def start_spark_consumer():
    try:
        # SparkSession 초기화 (JAR 파일 경로 추가)
        spark = SparkSession.builder \
            .appName("KafkaProtoBufConsumer") \
            .config("spark.jars.packages",
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,org.apache.kafka:kafka-clients:3.5.0") \
            .config("spark.hadoop.io.native.lib.available", "false") \
            .getOrCreate()

        print("[정보] PySpark가 Kafka 토픽에서 데이터를 소비 중...")

        # Kafka에서 dashboard_status 토픽 데이터 읽기
        df_dashboard = spark.readStream.format("kafka") \
            .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')) \
            .option("subscribe", "dashboard_status") \
            .option("startingOffsets", "earliest") \
            .load()

        # 데이터 역직렬화 (Protobuf을 JSON으로 변환)
        df_dashboard = df_dashboard.withColumn("value", deserialize_dashboard_proto_udf(df_dashboard["value"]))

        # monthly_volume_status 토픽 데이터 스트림 읽기
        df_monthly_volume = spark.readStream.format("kafka") \
            .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')) \
            .option("subscribe", "monthly_volume_status") \
            .option("startingOffsets", "earliest") \
            .load()

        # 데이터 역직렬화 (Protobuf을 JSON으로 변환)
        df_monthly_volume = df_monthly_volume.withColumn("value", deserialize_monthly_proto_udf(df_monthly_volume["value"]))

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
