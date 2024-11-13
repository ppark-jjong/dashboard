# from io import StringIO
#
# from google.cloud import storage
# from datetime import datetime, timedelta
# from src.config.config_manager import ConfigManager
# import pandas as pd
# import os
# import logging
#
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# logger = logging.getLogger(__name__)
#
# config = ConfigManager()
#
# # GCS 설정
# GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
# client = storage.Client()
# bucket = client.bucket(GCS_BUCKET_NAME)
#
#
# def save_to_gcs(dataframe, file_name):
#     blob = bucket.blob(file_name)
#     blob.upload_from_string(dataframe.to_csv(index=False), content_type="text/csv")
#     logger.info(f"GCS 버킷 {GCS_BUCKET_NAME}에 {file_name} 파일 저장 완료")
#
#
# def fetch_and_merge_data_from_gcs():
#     """
#     최근 데이터를 로드한 뒤 기존 데이터를 누적 병합하여 리턴합니다.
#     """
#     one_hour_ago = datetime.utcnow() - timedelta(hours=1)
#     blobs = bucket.list_blobs()
#     all_data = pd.DataFrame(columns=config.sheets.COLUMNS)
#
#     for blob in blobs:
#         timestamp_str = blob.name.split('_')[-1].replace('.csv', '')
#         try:
#             file_timestamp = datetime.strptime(timestamp_str, '%y%m%d-%H%M')
#             if file_timestamp >= one_hour_ago:
#                 data = blob.download_as_string().decode('utf-8')
#                 df = pd.read_csv(StringIO(data))
#                 all_data = pd.concat([all_data, df], ignore_index=True)
#         except ValueError:
#             continue
#
#     return all_data if not all_data.empty else None
