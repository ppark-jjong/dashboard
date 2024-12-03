from src.config.manager_config import ConfigManager
from pyspark.sql.functions import col, count, sum
from pathlib import Path

# 전역 변수 설정
MODE = "local"  # "local" 또는 "cloud"
LOCAL_PATH = "../../data/CS_Delivery Report.csv"  # 로컬 CSV 파일 경로
BUCKET_NAME = "your-bucket-name"  # GCS 버킷 이름
FILE_NAME = "data.csv"  # GCS 파일 이름
TEMP_DIR = "./data"  # GCS 파일 다운로드 임시 디렉토리
OUTPUT_DIR = "../../outputTest"  # 처리 결과 저장 경로


def load_local_data(sparkSession):
    try:
        print(f"로컬 데이터를 {LOCAL_PATH}에서 로드합니다.")
        return sparkSession.read.csv(LOCAL_PATH, header=True, inferSchema=True)
    except Exception as e:
        print(f"로컬 데이터 로드 실패: {e}")
        raise RuntimeError(f"로컬 데이터를 로드하는 중 오류가 발생했습니다: {e}")


def load_cloud_data(sparkSession):
    try:
        print(f"GCS 데이터를 {BUCKET_NAME}/{FILE_NAME}에서 로드합니다.")
        gcs_client = ConfigManager.get_gcs_client()
        bucket = gcs_client.bucket(BUCKET_NAME)
        blob = bucket.blob(FILE_NAME)

        # 로컬 임시 경로로 파일 다운로드
        temp_path = Path(TEMP_DIR) / FILE_NAME
        temp_path.parent.mkdir(parents=True, exist_ok=True)  # 디렉토리 생성
        blob.download_to_filename(temp_path)
        print(f"GCS에서 {FILE_NAME}을 {temp_path}로 다운로드했습니다.")

        # Spark DataFrame 로드
        return sparkSession.read.csv(temp_path, header=True, inferSchema=True)
    except Exception as e:
        print(f"GCS 데이터 로드 실패: {e}")
        raise RuntimeError(f"GCS 데이터를 로드하는 중 오류가 발생했습니다: {e}")


def process_and_save_data(sparkSession):
    try:
        # 데이터 로드
        if MODE == "local":
            df = load_local_data(sparkSession)
        elif MODE == "cloud":
            df = load_cloud_data(sparkSession)
        else:
            raise ValueError(f"알 수 없는 모드: {MODE}. 'local' 또는 'cloud' 중 하나여야 합니다.")

        # 데이터 전처리
        df = df.coalesce(4).cache()  # 파티션 수 제한 및 캐싱
        processed_df = df.filter(col("status") == "delivered") \
            .groupBy("status") \
            .agg(
                count("id").alias("total_orders"),
                sum("amount").alias("total_amount")
            )
        processed_df.show()
        df.unpersist()  # 캐시 해제

        # 처리 결과 저장
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        processed_df.write.mode("overwrite").json(str(output_dir))
        print(f"결과가 {OUTPUT_DIR}에 저장되었습니다.")
    except Exception as e:
        print(f"데이터 처리 실패: {e}")
        raise RuntimeError(f"데이터 처리 중 오류가 발생했습니다: {e}")

