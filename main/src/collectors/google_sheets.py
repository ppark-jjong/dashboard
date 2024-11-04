import json
from google.cloud import storage
import pandas as pd
import logging
from src.brokers.kafka.producer import create_kafka_producer, send_to_kafka
from src.config.config_google import SheetsConfig as config

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Google Sheets에서 데이터를 가져와 DataFrame으로 반환
def fetch_sheet_data():
    """
    Google Sheets에서 데이터를 가져와 DataFrame으로 변환하여 반환.
    SheetsConfig의 서비스 설정을 사용하며, 데이터가 없으면 None을 반환.
    """
    try:
        service = config.get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=config.SHEET_ID, range=config.RANGE_NAME).execute()
        rows = result.get('values', [])

        if not rows:
            logger.warning("Google Sheets에서 데이터를 찾을 수 없습니다.")
            return

        logger.info(f"{len(rows)}개의 데이터를 Google Sheets에서 가져왔습니다.")
        df = pd.DataFrame(rows[1:], columns=COLUMNS)  # 데이터프레임 생성
        return df
    except Exception as e:
        logger.error(f"Google Sheets 데이터 가져오기 실패: {e}")
        return None

# DataFrame 데이터를 GCS에 저장
def save_to_gcs(df):
    """
    DataFrame을 Google Cloud Storage(GCS)에 CSV 파일로 저장.
    저장 위치는 설정된 버킷 내, 타임스탬프가 포함된 파일 이름으로 지정됨.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
        blob = bucket.blob(f"realtime_data_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.csv")
        blob.upload_from_string(df.to_csv(index=False), 'text/csv')
        logger.info("Google Sheets 데이터가 GCS에 저장되었습니다.")
    except Exception as e:
        logger.error(f"GCS에 데이터 저장 실패: {e}")

# Google Sheets 데이터를 수집하여 Kafka와 GCS로 전송
def collect_and_send_data():
    """
    Google Sheets 데이터를 수집한 후 Kafka와 GCS로 전송.
    Kafka 토픽으로 데이터를 전송하고, GCS에도 데이터를 저장.
    """
    df = fetch_sheet_data()
    if df is not None and not df.empty:
        # Kafka로 전송
        producer = create_kafka_producer()
        topic = config.KAFKA_TOPICS['realtime_status']
        send_to_kafka(producer, topic, df)
        logger.info(f"Google Sheets 데이터가 '{topic}' 토픽으로 전송되었습니다.")

        # GCS에 저장
        save_to_gcs(df)

# Cloud Function을 통한 요청 처리 핸들러
def cloud_function_handler(request):
    """
    클라우드 함수로부터 요청을 받아 데이터 처리.
    요청 데이터에서 필요한 값을 추출하여 DataFrame으로 변환 후 전처리 및 Kafka, GCS에 전송.
    """
    try:
        # 요청에서 데이터 추출
        data = json.loads(request.data.decode('utf-8'))['data']

        # 데이터프레임 생성 및 컬럼 매핑
        df = pd.DataFrame([data], columns=COLUMNS)

        # 필요한 데이터 전처리 로직 추가
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # 날짜 형식 변환
        df['Status'] = df['Status'].fillna('Unknown')  # 결측값 처리

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
