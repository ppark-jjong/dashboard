import asyncio
from fastapi import FastAPI, Request, HTTPException
from src.config.config_manager import ConfigManager
# from google.cloud import storage
from src.kafka.producer import KafkaProducerService
import os
import json
import pandas as pd
import logging

# FastAPI 설정
app = FastAPI()

# 클라이언트 및 설정 초기화
# client = storage.Client()
config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
producer_service = KafkaProducerService()

# Topic 설정
KAFKA_TOPIC = config.kafka.TOPICS
RAW_TOPIC = config.kafka.RAW_TOPIC

# GCS 관련 설정
GCS_BUCKET_NAME = config.gcs.BUCKET_NAME
# bucket = client.bucket(GCS_BUCKET_NAME)
file_name = config.file_name


# 데이터 전처리 함수
def preprocess_status(data):
    # Picked, Shipped, POD 필드를 기반으로 Status를 표준화
    picked = data.get('Picked', '').upper() == 'O'
    shipped = data.get('Shipped', '').upper() == 'O'
    pod = data.get('POD', '').upper() == 'O'

    if picked and not shipped and not pod:
        return 'Picked'
    elif picked and shipped and not pod:
        return 'Shipped'
    elif picked and shipped and pod:
        return 'Delivered'
    else:
        return 'Unknown'


@app.post("/webhook")
# async def receive_data(request: Request):
async def receive_data():
    try:
        # 1. 데이터 수신
        # data = await request.json()
        # logger.info(f"수신된 원본 데이터: {data}")
        with open("data/data.json", "r") as file:
            data = json.load(file)
        print(data)

        # 2. DataFrame 변환
        df = pd.DataFrame(data, columns=config.sheets.COLUMNS)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.sort_values(by=['Date'], inplace=True)
        print(df.head())

        # 3. Status 전처리
        df['Status'] = df.apply(preprocess_status, axis=1)

        # 4. 비동기 작업 생성
        # GCS 저장 작업
        # gcs_save_task = save_to_gcs_async(df, config.file_name)
        # Kafka 전송 작업
        raw_topic_task = producer_service.kafka_produce_async(df.to_dict(orient='records'), RAW_TOPIC)

        # 5. 비동기 작업 병렬 실행
        results = await asyncio.gather(
            # gcs_save_task,
            raw_topic_task,
            return_exceptions=True  # 작업이 독립적으로 처리되도록 설정
        )

        # 6. 결과 처리
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"작업 {i + 1} 실패: {result}")
            else:
                logger.info(f"작업 {i + 1} 성공: {result}")

        return {"status": "success", "message": "작업 완료"}
    except Exception as e:
        logger.error(f"전체 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="데이터 처리 실패")


# async def save_to_gcs_async(dataframe, file_name):
#     try:
#         # GCS에 파일 저장
#         blob = bucket.blob(file_name)
#         blob.upload_from_string(dataframe.to_csv(index=False), content_type="text/csv")
#         logger.info(f"GCS 버킷 {config.gcs.BUCKET_NAME}에 {file_name} 파일 저장 완료")
#     except Exception as e:
#         logger.error(f"GCS 저장 실패: {e}")
#         raise
#
#
