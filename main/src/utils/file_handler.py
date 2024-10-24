from google.cloud import storage
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DataFrame을 GCS에 CSV 형식으로 저장
def save_to_gcs(df: pd.DataFrame, bucket_name: str, file_name: str, service_account_file: str):
    try:
        storage_client = storage.Client.from_service_account_json(service_account_file)  # GCS 클라이언트 생성
        bucket = storage_client.bucket(bucket_name)  # GCS 버킷 가져오기
        blob = bucket.blob(file_name)  # 파일 객체 생성

        blob.upload_from_string(df.to_csv(index=False), 'text/csv')  # DataFrame을 CSV로 변환 후 GCS에 업로드
        logger.info(f"GCS에 {file_name}로 데이터 저장 완료.")  # 저장 완료 로그
    except Exception as e:
        logger.error(f"GCS 업로드 중 오류 발생: {e}")  # 오류 발생 로그
