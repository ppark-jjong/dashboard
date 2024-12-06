from google.cloud import storage
from src.config import sheet_cofig

def upload_to_gcs(file_path, destination_blob_name):
    """
    GCS에 파일 업로드
    """
    client = storage.Client.from_service_account_json(config.GCS_SERVICE_ACCOUNT)
    bucket = client.bucket(config.GCS_BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)
    print(f"File {file_path} uploaded to {destination_blob_name}.")
