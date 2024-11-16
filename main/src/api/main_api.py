import asyncio

from fastapi import FastAPI, Request, HTTPException
from src.config.config_manager import ConfigManager
from google.cloud import storage
from src.kafka.producer import KafkaProducerService
import os
import json
import pandas as pd
import logging

app = FastAPI()
client = storage.Client()
config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
producer_service = KafkaProducerService()
KAFKA_TOPIC = config.kafka.TOPICS['dashboard_status']
GCS_BUCKET_NAME = config.gcs.BUCKET_NAME
bucket = client.bucket(GCS_BUCKET_NAME)
file_name = config.file_name


@app.post("/webhook")
async def receive_data(request: Request):
    try:
        # 1. 데이터 수신
        data = await request.json()
        logger.info(f"수신된 원본 데이터: {data}")

        # 2. DataFrame 변환
        df = pd.DataFrame(data['values'], columns=config.sheets.COLUMNS)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.sort_values(by=['Date'], inplace=True)

        # 3. 비동기 작업 생성
        gcs_save_task = save_to_gcs_async(df, config.file_name)  # GCS 저장 작업
        kafka_task =producer_service.kafka_produce_async(df)  # Kafka 전송 작업

        # 4. 비동기 작업 병렬 실행
        results = await asyncio.gather(
            gcs_save_task,
            kafka_task,
            return_exceptions=True  # 작업이 독립적으로 처리되도록 설정
        )

        # 5. 결과 처리
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"작업 {i + 1} 실패: {result}")
            else:
                logger.info(f"작업 {i + 1} 성공: {result}")

        return {"status": "success", "message": "작업 완료"}
    except Exception as e:
        logger.error(f"전체 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="데이터 처리 실패")


async def save_to_gcs_async(dataframe, file_name):
    try:
        blob = bucket.blob(file_name)
        blob.upload_from_string(dataframe.to_csv(index=False), content_type="text/csv")
        logger.info(f"GCS 버킷 {config.gcs.BUCKET_NAME}에 {file_name} 파일 저장 완료")
    except Exception as e:
        logger.error(f"GCS 저장 실패: {e}")
        raise




# GCS data
@app.get("/test-gcs-kafka")
async def test_gcs_kafka():
    try:
        # data.json 파일에서 데이터를 불러옴
        data_path = os.path.join("data", "data.json")
        with open(data_path, "r") as f:
            data = json.load(f)

        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        logger.info("data.json 파일로부터 데이터를 로드했습니다.")

        # Kafka에 데이터 전송 테스트
        producer_service.send_data(df)
        logger.info("Kafka에 데이터 전송 완료")

        return {"status": "success", "message": "GCS와 Kafka 테스트 완료"}

    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="테스트 실패")
