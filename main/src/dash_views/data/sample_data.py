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

    data = []
    for i in range(n):
        status = random.randint(0, 3)
        depart_time = datetime.now() + timedelta(hours=random.randint(-48, 48))
        arrive_time = depart_time + timedelta(minutes=random.randint(30, 180))
        delivery_duration = int((arrive_time - depart_time).total_seconds() / 60)

        record = {
            'department': random.choice(departments),
            'type': random.randint(0, 1),
            'driver': random.choice(drivers) if status > 0 else None,
            'dps': f"{random.randint(1000000000, 9999999999)}",
            'sla': f"{random.randint(1, 24)}시간",
            'eta': (datetime.now() + timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M'),
            'depart_time': depart_time.strftime('%Y-%m-%d %H:%M') if status > 0 else None,
            'arrive_time': arrive_time.strftime('%Y-%m-%d %H:%M') if status == 2 else None,
            'delivery_duration': delivery_duration,
            'address': f"{random.choice(addresses)} {random.randint(1, 100)}번길 {random.randint(1, 100)}",
            'recipient': f"홍길동{random.randint(1, 100)} / 010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            'status': status,
            'reason': random.choice(issue_reasons) if status == 3 else None
        }
        data.append(record)
    return data