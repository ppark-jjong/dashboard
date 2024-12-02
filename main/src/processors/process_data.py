from src.config.manager_config import ConfigManager
from pyspark.sql.functions import col, count, sum
from pathlib import Path


def load_local_data(spark, local_path="./data/dummy.csv"):
    """
    로컬 CSV 데이터를 로드합니다.
    :param spark: SparkSession
    :param local_path: 로컬 CSV 경로
    :return: Spark DataFrame
    """
    try:
        print(f"로컬 데이터를 {local_path}에서 로드합니다.")
        return spark.read.csv(local_path, header=True, inferSchema=True)
    except Exception as e:
        print(f"로컬 데이터 로드 실패: {e}")
        raise RuntimeError(f"로컬 데이터를 로드하는 중 오류가 발생했습니다: {e}")


def load_cloud_data(spark, bucket_name, file_name, temp_dir="./data"):
    """
    GCS에서 CSV 데이터를 로드합니다.
    :param spark: SparkSession
    :param bucket_name: GCS 버킷 이름
    :param file_name: GCS 파일 이름
    :param temp_dir: 로컬 임시 저장 디렉토리
    :return: Spark DataFrame
    """
    try:
        # GCS 클라이언트 생성
        gcs_client = ConfigManager.get_gcs_client()
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # 로컬 임시 경로로 파일 다운로드
        temp_path = Path(temp_dir) / file_name
        temp_path.parent.mkdir(parents=True, exist_ok=True)  # 디렉토리 생성
        blob.download_to_filename(temp_path)
        print(f"GCS에서 {file_name}을 {temp_path}로 다운로드했습니다.")

        # Spark DataFrame 로드
        return spark.read.csv(temp_path, header=True, inferSchema=True)
    except Exception as e:
        print(f"GCS 데이터 로드 실패: {e}")
        raise RuntimeError(f"GCS 데이터를 로드하는 중 오류가 발생했습니다: {e}")


def process_data(df):
    """
    데이터 전처리
    :param df: Spark DataFrame
    :return: 처리된 Spark DataFrame
    """
    df = df.coalesce(4).cache()  # 파티션 수 제한 및 캐싱
    processed_df = df.filter(col("status") == "delivered") \
        .groupBy("status") \
        .agg(
            count("id").alias("total_orders"),
            sum("amount").alias("total_amount")
        )
    processed_df.show()
    df.unpersist()  # 캐시 해제
    return processed_df


def save_results(df, output_path="./output/results"):
    """
    처리 결과 저장
    :param df: Spark DataFrame
    :param output_path: 저장 경로
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    df.write.mode("overwrite").json(str(output_dir))
    print(f"결과가 {output_path}에 저장되었습니다.")


def process_local_data():
    """
    로컬 데이터를 처리하는 메인 로직
    """
    try:
        # SparkSession 생성
        spark = ConfigManager.get_spark_session()

        # 로컬 데이터 로드
        local_path = "./data/dummy.csv"
        df = load_local_data(spark, local_path=local_path)

        # 데이터 전처리
        processed_df = process_data(df)

        # 결과 저장
        save_results(processed_df)
    except Exception as e:
        print(f"로컬 데이터 처리 실패: {e}")
    finally:
        # SparkSession 종료
        ConfigManager.stop_spark_session()


def process_cloud_data():
    """
    GCP 데이터를 처리하는 메인 로직
    """
    try:
        # SparkSession 생성
        spark = ConfigManager.get_spark_session()

        # GCS 데이터 로드
        bucket_name = "your-bucket-name"
        file_name = "data.csv"
        df = load_cloud_data(spark, bucket_name=bucket_name, file_name=file_name)

        # 데이터 전처리
        processed_df = process_data(df)

        # 결과 저장
        save_results(processed_df)
    except Exception as e:
        print(f"GCS 데이터 처리 실패: {e}")
    finally:
        # SparkSession 종료
        ConfigManager.stop_spark_session()


if __name__ == "__main__":
    mode = input("Enter mode ('local' or 'cloud'): ").strip().lower()

    if mode == "local":
        process_local_data()
    elif mode == "cloud":
        process_cloud_data()
    else:
        print("올바른 모드를 입력하세요: 'local' 또는 'cloud'")
