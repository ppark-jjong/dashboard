from pyspark.sql import SparkSession
from pyspark.sql.functions import col

try:
    # SparkSession 생성
    spark = SparkSession.builder \
        .appName("Kafka-Spark Consumer Test") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoints") \
        .getOrCreate()

    # 로그 레벨 설정
    spark.sparkContext.setLogLevel("INFO")

    # Kafka에서 데이터를 읽어옴
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:29092") \
        .option("subscribe", "test_topic") \
        .option("startingOffsets", "earliest") \
        .load()

    # Kafka 메시지 값 추출 및 콘솔 출력
    messages = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) as message")

    # 콘솔에 메시지 출력
    query = messages.writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    # 스트리밍 작업 대기
    query.awaitTermination()

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    spark.stop()
