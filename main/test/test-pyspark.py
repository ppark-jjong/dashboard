from pyspark.sql import SparkSession


def test_spark():
    # SparkSession 생성
    spark = SparkSession.builder \
        .appName("TestSpark") \
        .master("spark://spark-master:7077") \
        .getOrCreate()

    # 샘플 데이터 생성
    data = [("Alice", 34), ("Bob", 45), ("Cathy", 29)]
    columns = ["Name", "Age"]

    df = spark.createDataFrame(data, columns)
    df.show()

    # 나이 평균 계산
    df.groupBy().avg('Age').show()

    spark.stop()


if __name__ == "__main__":
    test_spark()
