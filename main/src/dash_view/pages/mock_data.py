from datetime import datetime, timedelta
import random


def generate_sample_data(n=100):
    departments = ['CS', 'HES', 'Lenovo']
    status_map = {0: '대기', 1: '진행', 2: '완료', 3: '이슈'}
    drivers = ['김운송', '이배달', '박퀵서비스', '최배송', '정기사']
    addresses = [
        '서울시 강남구', '서울시 서초구', '서울시 송파구',
        '경기도 성남시', '경기도 수원시', '인천시 연수구',
        '경기도 용인시', '서울시 마포구', '서울시 영등포구'
    ]
    issue_reasons = [
        '배송 지연', '주소지 오류', '고객 부재', '차량 문제',
        '교통 체증', '기상 악화', '고객 연락 불가'
    ]

    now = datetime.now()
    data = []

    # ETA 테스트를 위한 특수 데이터 추가
    special_cases = [
        # 10분 후 (임박)
        {
            'department': 'CS',
            'type': 0,
            'driver': '김운송',
            'status': 1,
            'eta': (now + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M')
        },
        # 20분 후 (임박)
        {
            'department': 'HES',
            'type': 0,
            'driver': '이배달',
            'status': 1,
            'eta': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M')
        },
        # 10분 전 (초과)
        {
            'department': 'Lenovo',
            'type': 1,
            'driver': '박퀵서비스',
            'status': 1,
            'eta': (now - timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M')
        },
        # 30분 전 (초과)
        {
            'department': 'CS',
            'type': 1,
            'driver': '최배송',
            'status': 1,
            'eta': (now - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M')
        }
    ]

    # 특수 케이스 데이터 추가
    for case in special_cases:
        data.append({
            'department': case['department'],
            'type': case['type'],
            'driver': case['driver'],
            'dps': f"{random.randint(1000000000, 9999999999)}",
            'sla': f"{random.randint(1, 24)}시간",
            'eta': case['eta'],
            'status': case['status'],
            'address': f"{random.choice(addresses)} {random.randint(1, 100)}번길 {random.randint(1, 100)}",
            'recipient': f"홍길동{random.randint(1, 100)} / 010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            'reason': None
        })

    # 나머지 일반 데이터 생성
    for i in range(n - len(special_cases)):
        status = random.randint(0, 3)
        # 정상 배송 시간대 (현재시각 기준 1~48시간 사이)
        eta = now + timedelta(hours=random.randint(1, 48))

        record = {
            'department': random.choice(departments),
            'type': random.randint(0, 1),
            'driver': random.choice(drivers) if status > 0 else None,
            'dps': f"{random.randint(1000000000, 9999999999)}",
            'sla': f"{random.randint(1, 24)}시간",
            'eta': eta.strftime('%Y-%m-%d %H:%M'),
            'address': f"{random.choice(addresses)} {random.randint(1, 100)}번길 {random.randint(1, 100)}",
            'recipient': f"홍길동{random.randint(1, 100)} / 010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            'status': status,
            'reason': random.choice(issue_reasons) if status == 3 else None
        }
        data.append(record)

    return data