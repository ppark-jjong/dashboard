# data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def generate_delivery_data(n_rows=50):
    current_time = datetime.now()
    drivers = [f'드라이버_{i:02d}' for i in range(1, 6)]

    return pd.DataFrame({
        'OperationType': np.random.choice(['배송', '회수'], n_rows),
        'Department': np.random.choice(['물류1팀', '물류2팀', '물류3팀', '특송팀'], n_rows),
        'Driver': np.random.choice(drivers, n_rows),
        'DPS': [f'DPS{i:04d}' for i in range(1, n_rows + 1)],
        'Status': np.random.choice(['대기', '배송중', '배송완료'], n_rows),
        'ETA': [(current_time + timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M') for _ in
                range(n_rows)],
        'DepartTime': [(current_time + timedelta(minutes=random.randint(30, 120))).strftime('%H:%M') for _ in
                       range(n_rows)],
        'SLA': np.random.choice(['일반', '프리미엄', '익일'], n_rows),
        'Address': np.random.choice([
            '서울특별시 강남구 테헤란로 123 올림피아빌딩 15층',
            '경기도 성남시 분당구 판교역로 235 에이치스퀘어 N동',
            '서울특별시 송파구 올림픽로 300 롯데월드타워 35층'
        ], n_rows),
        'Recipient': [f'수령인_{i:02d}' for i in range(1, n_rows + 1)]
    })


def generate_driver_data(n_rows=20):
    current_time = datetime.now()

    return pd.DataFrame({
        'Name': [f'드라이버_{i:02d}' for i in range(1, n_rows + 1)],
        'Status': np.random.choice(['운행중', '대기중', '휴식'], n_rows),
        'ArrivalTime': [(current_time + timedelta(minutes=random.randint(10, 60))).strftime('%H:%M') for _ in
                        range(n_rows)],
        'VehicleType': np.random.choice(['1톤 트럭', '2.5톤 트럭', '오토바이', '다마스'], n_rows),
        'Qty': np.random.randint(1, 50, n_rows)
    })