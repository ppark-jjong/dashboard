from google.cloud import storage
import os

# GCP 서비스 계정 키 파일 경로 설정 (환경 변수로 설정)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/MyMain/dashboard/main/oauth/google/credentials.json'  # 서비스 계정 키 경로 설정


# GCS에 파일 업로드
def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()  # GCS 클라이언트 생성
    bucket = storage_client.bucket(bucket_name)  # 버킷 가져오기
    blob = bucket.blob(destination_blob_name)  # 업로드할 Blob 객체 생성

    blob.upload_from_filename(source_file_name)  # 로컬 파일을 GCS에 업로드
    print(f"파일 {source_file_name}이(가) {bucket_name}의 {destination_blob_name}으로 업로드되었습니다.")  # 업로드 완료 메시지 출력


# GCS에서 파일 다운로드
def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()  # GCS 클라이언트 생성
    bucket = storage_client.bucket(bucket_name)  # 버킷 가져오기
    blob = bucket.blob(source_blob_name)  # 다운로드할 Blob 객체 생성

    blob.download_to_filename(destination_file_name)  # GCS 파일을 로컬로 다운로드
    print(f"{bucket_name}의 {source_blob_name}이(가) 로컬 파일 {destination_file_name}으로 다운로드되었습니다.")  # 다운로드 완료 메시지 출력


if __name__ == "__main__":
    bucket_name = "teckwah-data"  # 이미 생성된 GCS 버킷 이름
    source_file_name = "C:/Users/RMA2/Desktop/new/test.txt"  # 업로드할 로컬 파일 경로 (예: C:/data/test_upload.txt)
    destination_blob_name = "uploaded_test_file.txt"  # GCS에 저장할 파일 이름

    # 파일 업로드
    try:
        upload_to_gcs(bucket_name, source_file_name, destination_blob_name)  # 파일 업로드 호출
    except Exception as e:
        print(f"파일 업로드 중 오류 발생: {e}")  # 오류 발생 시 메시지 출력

    download_file_name = "C:/Users/RMA2/Desktop/new/download_test.txt"  # 다운로드할 로컬 파일 경로 (예: C:/data/downloaded_test_file.txt)

    # 파일 다운로드
    try:
        download_from_gcs(bucket_name, destination_blob_name, download_file_name)  # 파일 다운로드 호출
    except Exception as e:
        print(f"파일 다운로드 중 오류 발생: {e}")  # 오류 발생 시 메시지 출력
