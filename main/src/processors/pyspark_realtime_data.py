import pandas as pd
import logging
from datetime import datetime

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Kafka에서 가져온 데이터를 전처리하여 오늘과 미래의 데이터를 분리
def process_data(records):
    df = pd.DataFrame(records)

    # ETA 열을 datetime으로 변환하고, 현재 날짜와 비교
    df['ETA'] = pd.to_datetime(df['ETA'], errors='coerce')
    today = pd.Timestamp(datetime.now().date())

    # 오늘의 ETA와 미래 ETA를 구분
    today_data = df[df['ETA'] == today]
    future_data = df[df['ETA'] > today]

    logger.info(f"오늘 데이터: {len(today_data)}건, 미래 데이터: {len(future_data)}건")
    return today_data, future_data

