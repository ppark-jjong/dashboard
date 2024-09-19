from pyspark.sql import SparkSession

# Spark 세션 생성
spark = SparkSession.builder.appName("Simple Test").getOrCreate()

# 데이터 로드 및 확인
data = [("Alice", 25), ("Bob", 30), ("Catherine", 29)]
df = spark.createDataFrame(data, ["Name", "Age"])

df.show()

# 나이 필터링
filtered_df = df.filter(df.Age > 28)
filtered_df.show()

# Spark 세션 종료
spark.stop()
