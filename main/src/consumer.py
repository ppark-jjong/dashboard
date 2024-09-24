from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType
import delivery_status_pb2

def start_spark_streaming():
    """PySpark를 사용하여 Kafka에서 데이터를 소비하고 처리하는 함수"""
    # Spark 세션 생성
    spark = SparkSession.builder \
        .appName("DeliveryStatusConsumer") \
        .getOrCreate()

    # Kafka 설정
    KAFKA_TOPIC = "delivery_status"
    KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

    # Proto 역직렬화 함수 정의
    def deserialize_proto(data):
        """Proto 메시지를 역직렬화하는 함수"""
        try:
            delivery_status = delivery_status_pb2.DeliveryStatus()
            delivery_status.ParseFromString(data)
            # 결과를 문자열로 반환
            return f"주문ID: {delivery_status.order_id}, 고객명: {delivery_status.customer_name}, 주소: {delivery_status.delivery_address}, 상태: {delivery_status.status}, 시간: {delivery_status.timestamp}"
        except Exception as e:
            return f"역직렬화 중 오류 발생: {e}"

    # UDF로 등록
    deserialize_udf = udf(lambda x: deserialize_proto(x), StringType())

    # Kafka에서 메시지를 소비하는 데이터 프레임 생성
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .load()

    # 메시지를 역직렬화
    df_parsed = df.select(deserialize_udf(col("value")).alias("message"))

    # 처리된 데이터를 콘솔에 출력
    query = df_parsed.writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    # 오류 및 상태 로그 모니터링
    query.awaitTermination()
