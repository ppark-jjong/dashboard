import logging
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from src.config.config_manager import ConfigManager
from google.cloud import storage
from src.collectors.google_sheets import save_to_gcs
from src.kafka.producer import create_kafka_producer, send_to_kafka

app = FastAPI()
config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
producer = create_kafka_producer()
KAFKA_TOPIC = config.kafka.TOPIC
config = ConfigManager()
GCS_BUCKET_NAME = config.gcs.BUCKET_NAME
client = storage.Client()
bucket = client.bucket(GCS_BUCKET_NAME)
file_name = config.gcs.file_name


@app.post("/webhook")
async def receive_data(request: Request):
    try:
        data = await request.json()
        logger.info(f"수신된 원본 데이터: {data}")

        # DataFrame 생성 및 컬럼 이름 매핑
        df = pd.DataFrame(data['values'], columns=config.sheets.COLUMNS)

        # 전처리
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Status'] = df['Status'].fillna('Unknown')
        df.sort_values(by=['Date'], inplace=True)

        save_to_gcs(df, file_name)

        return {"status": "success", "message": "Data processed and saved to GCS"}

    except KeyError as e:
        logger.error(f"필수 컬럼이 누락되었습니다: {e}")
        raise HTTPException(status_code=400, detail=f"필수 컬럼이 누락되었습니다: {e}")
    except Exception as e:
        logger.error(f"데이터 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="데이터 처리 실패")


@app.post("/run-kafka-process")
async def run_kafka_process():
    try:
        # GCS에 저장된 파일 지정
        blob = bucket.blob(file_name)

        # GCS에서 파일 데이터 읽기
        data = blob.download_as_text()

        # Kafka로 데이터 전송
        send_to_kafka(data)

        return {"status": "success", "message": "Data sent to Kafka"}

    except Exception as e:
        logger.error(f"GCS에서 Kafka로 데이터 전송 중 오류 발생: {e}")
        return {"status": "error", "message": str(e)}
