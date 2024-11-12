# src/api/main_api.py
from fastapi import FastAPI, Request, HTTPException
from src.config.config_manager import ConfigManager
from src.collectors.google_sheets import save_to_gcs
from src.kafka.producer import KafkaProducerService
import pandas as pd
import logging
import json
from google.cloud import storage
from datetime import datetime

app = FastAPI()
config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# GCS 및 Kafka 설정
client = storage.Client()
producer_service = KafkaProducerService()  # Kafka Producer 생성
bucket_name = config.gcs.BUCKET_NAME
bucket = client.bucket(bucket_name)
file_name = config.file_name


@app.post("/webhook")
async def receive_data(request: Request):
    """
    Webhook 요청을 통해 데이터를 수신하여 GCS에 저장하는 엔드포인트
    """
    try:
        data = await request.json()
        logger.info(f"수신된 원본 데이터: {data}")

        # DataFrame 생성 및 컬럼 이름 매핑
        df = pd.DataFrame(data['values'], columns=config.sheets.COLUMNS)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Status'] = df['Status'].fillna('Unknown')
        df.sort_values(by=['Date'], inplace=True)

        # GCS에 데이터 저장
        save_to_gcs(df, file_name)
        logger.info(f"GCS에 {file_name}으로 데이터 저장 완료")

        return {"status": "success", "message": "Data saved to GCS"}

    except Exception as e:
        logger.error(f"데이터 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="데이터 처리 실패")


@app.get("/load-data-and-send-to-kafka")
async def load_data_and_send_to_kafka():
    """
    지정된 파일을 로드하여 Kafka로 전송하는 엔드포인트
    """
    try:
        with open("data/data.json", "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)

        # Kafka 전송
        producer_service.send_data(df)
        logger.info("Kafka로 데이터 전송 완료")

        return {"status": "success", "message": "Data loaded from data.json and sent to Kafka"}
    except Exception as e:
        logger.error(f"Kafka로 데이터 전송 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="Kafka 전송 실패")
