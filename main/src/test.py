from pyspark.sql import SparkSession

# Spark 세션 생성
def test_spark_session():
    try:
        # Spark 세션을 생성
        spark = SparkSession.builder \
            .appName("SparkDockerTest") \
            .master("spark://spark-master:7077") \
            .getOrCreate()

        # 간단한 DataFrame 생성
        data = [("Alice", 1), ("Bob", 2), ("Cathy", 3)]
        df = spark.createDataFrame(data, ["Name", "Value"])

        # DataFrame 출력
        print("DataFrame 출력:")
        df.show()

        # 간단한 연산 수행
        print("값의 합계 계산:")
        df_sum = df.groupBy().sum("Value").collect()[0][0]
        print(f"Sum of values: {df_sum}")

        # Spark 세션 종료
        spark.stop()
        print("Spark가 정상적으로 작동합니다.")

    except Exception as e:
        print(f"Spark 테스트 실패: {e}")

if __name__ == "__main__":
    test_spark_session()
