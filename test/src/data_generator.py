# data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def search_dataframe(df, search_term):
    """데이터프레임 검색 함수"""
    if not search_term:
        return df
    return df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]


def generate_delivery_data(n_rows=100):
    current_time = datetime.now()
    departments = ['물류1팀', '물류2팀', '물류3팀', '특송팀']
    addresses = [
        '서울특별시 강남구 테헤란로 123길 45 삼성물산빌딩 지하 1층 물류센터',
        '경기도 성남시 분당구 판교역로 235번길 32 카카오엔터프라이즈 3층 창고',
        '서울특별시 송파구 올림픽로 300 롯데월드몰 지하 2층 배송센터',
        '인천광역시 연수구 컨벤시아대로 165 포스코타워 송도 지하 1층 창고',
        '서울특별시 영등포구 여의대로 108 파크원타워 지하 3층 배송센터'
    ]

    # ETA를 현재 시각 기준으로 생성
    eta_times = [current_time + timedelta(minutes=random.randint(10, 1440)) for _ in range(n_rows)]
    eta_strings = [eta.strftime('%Y-%m-%d %H:%M') for eta in eta_times]

    df = pd.DataFrame({
        'OperationType': np.random.choice(['배송', '회수'], size=n_rows),
        'Department': np.random.choice(departments, size=n_rows),
        'DPS': [f'DPS{i:06d}' for i in range(1, n_rows + 1)],
        'SLA': np.random.choice(['일반', '프리미엄', '익일'], size=n_rows),
        'ETA': eta_strings,
        'Address': np.random.choice(addresses, size=n_rows),
        'Status': np.random.choice(['대기', '배송중', '배송완료'], size=n_rows),
        'DepartTime': [(current_time + timedelta(minutes=random.randint(30, 180))).strftime('%H:%M') for _ in
                       range(n_rows)],
        'Driver': [f'드라이버_{i:03d}' for i in range(1, n_rows + 1)],
        'Recipient': [f'수령인_{i:03d}' for i in range(1, n_rows + 1)]
    })

    # ETA를 datetime으로 변환하여 정렬에 사용
    df['ETA_datetime'] = pd.to_datetime(df['ETA'])
    df = df.sort_values('ETA_datetime')
    df = df.drop('ETA_datetime', axis=1)

    return df


def generate_driver_data(n_rows=100):
    current_time = datetime.now()
    vehicle_types = ['1톤 트럭', '2.5톤 트럭', '오토바이', '다마스']

    df = pd.DataFrame({
        'Name': [f'드라이버_{i:03d}' for i in range(1, n_rows + 1)],
        'Status': np.random.choice(['운행중', '대기중', '휴식', '수리중'], size=n_rows),
        'ArrivalTime': [(current_time + timedelta(minutes=random.randint(10, 120))).strftime('%H:%M') for _ in
                        range(n_rows)],
        'VehicleType': np.random.choice(vehicle_types, size=n_rows),
        'Qty': np.random.randint(1, 100, size=n_rows)
    })
    return df