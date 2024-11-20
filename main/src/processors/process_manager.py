import pandas as pd
import logging
from datetime import datetime

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class ProcessManager:
    

# 데이터 전처리 함수
def preprocess_status(data):
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
