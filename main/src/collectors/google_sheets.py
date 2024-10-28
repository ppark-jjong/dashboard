import json
import os
from google.cloud import storage
import pandas as pd
import logging
from src.kafka.producer import create_kafka_producer, send_to_kafka
from src.config.config_manager import ConfigManager

config = ConfigManager()

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

COLUMNS = [
    '주문번호', 'Date(접수일)', 'DPS#', 'ETA', 'SLA', 'Ship to (2)',
    'Status', '1. Picked', '2. Shipped', '3. POD', 'Zip Code',
    'Billed Distance (Put into system)', '인수자', 'issue'
]

# Google Sheets에서 데이터를 가져와 DataFrame으로 반환
def fetch_sheet_data():
    try:
        service = config.get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=config.SHEET_ID, range=config.RANGE_NAME).execute()
        rows = result.get('values', [])

        if not rows:
            logger.warning("Google Sheets에서 데이터를 찾을 수 없습니다.")
            return None

        logger.info(f"{len(rows)}개의 데이터를 Google Sheets에서 가져왔습니다.")
        df = pd.DataFrame(rows[1:], columns=COLUMNS)
        return df
    except Exception as e:
        logger.error(f"Google Sheets 데이터 가져오기 실패: {e}")
        return None

# DataFrame 데이터를 GCS에 저장
def save_to_gcs(df):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
        blob = bucket.blob(f"realtime_data_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.csv")
        blob.upload_from_string(df.to_csv(index=False), 'text/csv')
        logger.info("Google Sheets 데이터가 GCS에 저장되었습니다.")
    except Exception as e:
        logger.error(f"GCS에 데이터 저장 실패: {e}")

# Google Sheets 데이터를 수집하여 Kafka와 GCP로 전송
def collect_and_send_data():
    df = fetch_sheet_data()
    if df is not None and not df.empty:
        # Kafka로 전송
        producer = create_kafka_producer()
        topic = config.KAFKA_TOPICS['realtime_status']
        send_to_kafka(producer, topic, df)
        logger.info(f"Google Sheets 데이터가 '{topic}' 토픽으로 전송되었습니다.")

        # GCS에 저장
        save_to_gcs(df)

# Cloud Functions 핸들러
def cloud_function_handler(request):
    try:
        # 요청에서 데이터 추출
        data = json.loads(request.data.decode('utf-8'))['data']
        df = pd.DataFrame([data], columns=COLUMNS)

        # 데이터를 Kafka로 전송
        producer = create_kafka_producer()
        topic = config.KAFKA_TOPICS['realtime_status']
        send_to_kafka(producer, topic, df)

        # GCS에 데이터 저장
        save_to_gcs(df)

        return {
            'statusCode': 200,
            'body': json.dumps('Data processed successfully')
        }

    except Exception as e:
        logger.error(f"데이터 처리 중 오류 발생: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing data: {str(e)}')
        }
