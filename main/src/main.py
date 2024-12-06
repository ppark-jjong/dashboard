from src.services.pyspark_service import create_spark_session
from src.services.gcs_service import upload_to_gcs

def main():
    # PySpark 세션 생성
    spark = create_spark_session()

    # 데이터 처리 로직 (예제)
    data = [("Alice", 29), ("Bob", 31), ("Cathy", 25)]
    columns = ["Name", "Age"]
    df = spark.createDataFrame(data, columns)
    df.show()

    # 로컬 파일 저장 및 GCS 업로드
    file_path = "output/example.csv"
    df.write.csv(file_path)
    upload_to_gcs(file_path, "example/example.csv")

if __name__ == "__main__":
    main()
