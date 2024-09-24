from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os

os.environ[
    'PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 pyspark-shell'

# SparkSession 생성
spark = SparkSession.builder \
    .appName("KafkaPySparkTest") \
    .master("local[*]") \
    .getOrCreate()

kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:29092") \
    .option("subscribe", "test_topic") \
    .load()

# Kafka 메시지를 문자열로 변환
messages_df = kafka_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# 메시지 출력
query = messages_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# 스트리밍 종료를 대기
query.awaitTermination()
