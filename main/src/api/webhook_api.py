# webhook_api.py
import os
import logging
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from src.brokers.kafka.producer import create_kafka_producer, send_to_kafka
from src.config.config_manager import ConfigManager

app = FastAPI()
config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

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

        # Kafka로 데이터 전송
        producer = create_kafka_producer()
        topic = config.kafka.TOPICS['realtime_status']
        send_to_kafka(producer, topic, df)
        logger.info("Kafka로 데이터 전송 완료")

        return {"status": "success", "message": "Data processed and sent to Kafka"}

    except KeyError as e:
        logger.error(f"필수 컬럼이 누락되었습니다: {e}")
        raise HTTPException(status_code=400, detail=f"필수 컬럼이 누락되었습니다: {e}")
    except Exception as e:
        logger.error(f"데이터 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="데이터 처리 실패")
