import os

import uvicorn
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
        # 수신된 JSON 데이터 로깅
        data = await request.json()
        logger.info(f"수신된 원본 데이터: {data}")  # 원본 JSON 데이터 확인

        # 데이터프레임 생성 및 로깅
        df = pd.DataFrame(data['data'], columns=['주문번호', 'Date(접수일)', 'DPS#', 'ETA', 'SLA', 'Ship to (2)',
                                                 'Status', '1. Picked', '2. Shipped', '3. POD', 'Zip Code',
                                                 'Billed Distance (Put into system)', '인수자', 'issue'])
        logger.info(f"DataFrame 생성 결과: {df.head()}")  # DataFrame 상위 5개 행 확인

        # Kafka Producer 생성 및 데이터 전송
        producer = create_kafka_producer()
        topic = config.kafka.TOPICS['realtime_status']
        logger.info(f"Kafka 토픽: {topic}로 데이터 전송을 시도합니다.")  # Kafka 토픽 정보 확인
        send_to_kafka(producer, topic, df)
        logger.info("Kafka로 데이터 전송 완료")  # Kafka 전송 성공 로그

        return {"status": "success", "message": "Data sent to Kafka"}
    except Exception as e:
        logger.error(f"Kafka 전송 중 오류 발생: {e}")  # 에러 로깅
        raise HTTPException(status_code=500, detail="데이터 처리 실패")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # 환경 변수에서 PORT를 가져오고, 기본값은 8080으로 설정
    uvicorn.run(app, host="0.0.0.0", port=port)
