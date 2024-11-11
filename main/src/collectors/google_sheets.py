import logging
import os
from google.cloud import storage

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
# GCS 설정
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
client = storage.Client()
bucket = client.bucket(GCS_BUCKET_NAME)


def save_to_gcs(dataframe, file_name):
    blob = bucket.blob(file_name)
    blob.upload_from_string(dataframe.to_csv(index=False), content_type="text/csv")
    logger.info(f"GCS 버킷 {GCS_BUCKET_NAME}에 {file_name} 파일 저장 완료")

