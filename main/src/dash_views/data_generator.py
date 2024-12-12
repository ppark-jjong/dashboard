# data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def get_test_addresses():
    """테스트용 주소 목록"""
    return [
        '서울시 강남구 테헤란로 123 강남빌딩 2층',
        '서울시 송파구 올림픽로 300 롯데월드몰 지하 2층',
        '경기도 성남시 분당구 판교역로 235 에이치스퀘어 N동 8층',
        '서울시 영등포구 여의대로 108 파크원타워 3층',
        '서울시 마포구 양화로 45 메세나폴리스 10층',
        '경기도 하남시 미사대로 750 스타필드 하남 1층',
        '인천시 연수구 센트럴로 123 상생프라자 5층',
        '서울시 서초구 반포대로 235 반포쇼핑몰 B1',
        '경기도 고양시 일산동구 호수로 731 웨스턴돔 3층',
        '서울시 종로구 종로 33 그랑서울 2층'
    ]


def get_test_recipients():
    """테스트용 수령인 목록"""
    return [
        {'name': '김철수', 'contact': '010-1234-5678'},
        {'name': '이영희', 'contact': '010-2345-6789'},
        {'name': '박지성', 'contact': '010-3456-7890'},
        {'name': '최민수', 'contact': '010-4567-8901'},
        {'name': '정수연', 'contact': '010-5678-9012'},
        {'name': '강민희', 'contact': '010-6789-0123'},
        {'name': '윤서준', 'contact': '010-7890-1234'},
        {'name': '임현주', 'contact': '010-8901-2345'},
        {'name': '신동욱', 'contact': '010-9012-3456'},
        {'name': '한미영', 'contact': '010-0123-4567'}
    ]


def get_available_drivers():
    """테스트용 기사 목록"""
    return [
        {'id': 'DRV001', 'name': '김기사', 'status': '대기중'},
        {'id': 'DRV002', 'name': '이기사', 'status': '운행중'},
        {'id': 'DRV003', 'name': '박기사', 'status': '대기중'},
        {'id': 'DRV004', 'name': '최기사', 'status': '운행중'},
        {'id': 'DRV005', 'name': '정기사', 'status': '휴식중'}
    ]


def generate_delivery_data(n_rows=20):  # 기본값을 20개로 변경
    """배송 데이터 생성"""
    current_time = datetime.now()
    addresses = get_test_addresses()
    recipients = get_test_recipients()
    drivers = get_available_drivers()
    departments = ['물류1팀', '물류2팀', '물류3팀', '특송팀']
    status_options = ['대기', '배송중', '배송완료']
    sla_options = ['일반', '프리미엄', '익일']

    data = []
    for i in range(n_rows):
        # 랜덤 시간 생성 (현재 시간 기준 ±6시간)
        random_hours = random.uniform(-6, 6)
        eta = current_time + timedelta(hours=random_hours)
        depart_time = eta - timedelta(minutes=random.randint(30, 180))

        recipient = random.choice(recipients)
        driver = random.choice(drivers)

        delivery = {
            'DeliveryID': f'DEL{i + 1:04d}',
            'OperationType': random.choice(['배송', '회수']),
            'Department': random.choice(departments),
            'DPS': f'DPS{i + 1:06d}',
            'SLA': random.choice(sla_options),
            'ETA': eta.strftime('%Y-%m-%d %H:%M'),
            'Address': random.choice(addresses),
            'Status': random.choice(status_options),
            'DepartTime': depart_time.strftime('%H:%M'),
            'Driver': driver['id'] if random.random() > 0.3 else None,  # 30% 확률로 미배정
            'Recipient': recipient['name'],
            'ContactNumber': recipient['contact']
        }
        data.append(delivery)

    return pd.DataFrame(data)


def search_dataframe(df, search_term, filters=None):
    """데이터프레임 검색 및 필터링"""
    if filters is None:
        filters = {}

    result_df = df.copy()

    # 검색어 필터링
    if search_term:
        mask = pd.Series(False, index=df.index)
        for col in df.columns:
            mask |= df[col].astype(str).str.contains(str(search_term), case=False, na=False)
        result_df = result_df[mask]

    # ETA 필터
    if filters.get('eta'):
        hours = int(filters['eta'])
        current_time = datetime.now()
        result_df['ETA_datetime'] = pd.to_datetime(result_df['ETA'])
        result_df = result_df[result_df['ETA_datetime'] <= (current_time + timedelta(hours=hours))]
        result_df = result_df.drop('ETA_datetime', axis=1)

    # 기타 필터 적용
    for key in ['driver', 'sla', 'department']:
        if filters.get(key):
            result_df = result_df[result_df[key.title()] == filters[key]]

    return result_df


def save_delivery_data(data):
    """배송 데이터 저장 (메모리에 임시 저장)"""
    global current_delivery_data
    current_delivery_data = data
    return True


# 전역 변수로 현재 데이터 저장
current_delivery_data = None