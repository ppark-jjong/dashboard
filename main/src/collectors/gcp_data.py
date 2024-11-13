from google.cloud import storage
from datetime import datetime, timedelta
from src.config.config_manager import ConfigManager
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

config = ConfigManager()

# GCS 설정
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
client = storage.Client()
bucket = client.bucket(GCS_BUCKET_NAME)


def save_to_gcs(dataframe, file_name):
    blob = bucket.blob(file_name)
    blob.upload_from_string(dataframe.to_csv(index=False), content_type="text/csv")
    logger.info(f"GCS 버킷 {GCS_BUCKET_NAME}에 {file_name} 파일 저장 완료")


def fetch_recent_file_from_gcs():
    """
    현재 시간 기준으로 1시간 이내에 생성된 파일을 GCS에서 가져옴.
    """
    try:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        blobs = bucket.list_blobs()

        # 파일명에서 타임스탬프 추출 및 조건에 맞는 파일 필터링
        recent_files = []
        for blob in blobs:
            timestamp_str = blob.name.split('_')[-1].replace('.csv', '')
            try:
                file_timestamp = datetime.strptime(timestamp_str, '%y%m%d-%H%M')
                if file_timestamp >= one_hour_ago:
                    recent_files.append(blob)
            except ValueError:
                continue

        if recent_files:
            latest_blob = sorted(recent_files, key=lambda x: x.time_created, reverse=True)[0]
            data = latest_blob.download_as_string().decode('utf-8')
            df = pd.read_csv(StringIO(data))
            logger.info(f"{latest_blob.name} 파일을 로드했습니다.")
            return df
        else:
            logger.info("조건에 맞는 파일이 없습니다.")
            return None

    except Exception as e:
        logger.error(f"GCS에서 파일을 가져오는 중 오류 발생: {e}")
        return None