from fastapi import FastAPI, Request, HTTPException
import logging
import pandas as pd
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
        df = pd.DataFrame(data['data'], columns=['주문번호', 'Date(접수일)', 'DPS#', 'ETA', 'SLA', 'Ship to (2)',
                                                 'Status', '1. Picked', '2. Shipped', '3. POD', 'Zip Code',
                                                 'Billed Distance (Put into system)', '인수자', 'issue'])

        producer = create_kafka_producer()
        topic = config.kafka.TOPICS['realtime_status']
        send_to_kafka(producer, topic, df)
        logger.info("Google Sheets 데이터가 Kafka로 전송되었습니다.")

        return {"status": "success", "message": "Data sent to Kafka"}
    except Exception as e:
        logger.error(f"Kafka로 데이터 전송 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="데이터 처리 실패")
