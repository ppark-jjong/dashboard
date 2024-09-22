from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import delivery_pb2

def deserialize_proto(byte_array):
    delivery = delivery_pb2.DeliveryData()
    delivery.ParseFromString(byte_array)
    return (delivery.date, delivery.status, delivery.billed_distance, delivery.issue)

if __name__ == '__main__':
    spark = SparkSession.builder \
        .appName("KafkaSparkConsumer") \
        .getOrCreate()

    # Kafka에서 스트리밍 데이터 읽기
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "delivery_topic") \
        .option("startingOffsets", "latest") \
        .load()

    # ProtoBuf 역직렬화를 위한 UDF 생성
    schema = StructType([
        StructField("date", StringType()),
        StructField("status", StringType()),
        StructField("billed_distance", DoubleType()),
        StructField("issue", StringType())
    ])

    deserialize_udf = udf(deserialize_proto, schema)

    # Kafka 메시지의 value를 역직렬화하여 DataFrame 생성
    df_parsed = df.select(deserialize_udf(col("value")).alias("data")).select("data.*")

    # 데이터 처리 로직 (예: 콘솔에 출력)
    query = df_parsed.writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    query.awaitTermination()
