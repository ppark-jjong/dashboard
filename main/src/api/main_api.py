from fastapi import FastAPI, Request, HTTPException
from src.config.config_manager import ConfigManager
# from google.cloud import storage
# from src.collectors.gcp_data import save_to_gcs
from src.kafka.producer import KafkaProducerService
import os
import json
import pandas as pd
import logging

app = FastAPI()
# client = storage.Client()
config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
producer_service = KafkaProducerService()
KAFKA_TOPIC = config.kafka.TOPICS['dashboard_status']
GCS_BUCKET_NAME = config.gcs.BUCKET_NAME
# bucket = client.bucket(GCS_BUCKET_NAME)
file_name = config.file_name

# @app.post("/webhook")
# async def receive_data(request: Request):
#     try:
#         data = await request.json()
#         logger.info(f"수신된 원본 데이터: {data}")
#
#         df = pd.DataFrame(data['values'], columns=config.sheets.COLUMNS)
#         df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
#         df.sort_values(by=['Date'], inplace=True)
#
#         # GCS에 데이터 저장만 수행
#         save_to_gcs(df, file_name)
#         return {"status": "success", "message": "Data saved to GCS"}
#
#     except Exception as e:
#         logger.error(f"데이터 처리 중 오류 발생: {e}")
#         raise HTTPException(status_code=500, detail="데이터 처리 실패")


# @app.get("/send-data-to-kafka")
# async def send_data_to_kafka():
#     try:
#         dummy_data = load_dummy_data_from_gcs(file_name)
#         send_to_kafka(producer, KAFKA_TOPIC, dummy_data)
#         return {"status": "success", "message": "Dummy data sent to Kafka"}
#
#     except Exception as e:
#         logger.error(f"Kafka로 데이터 전송 중 오류 발생: {e}")
#         raise HTTPException(status_code=500, detail="Kafka 전송 실패")

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