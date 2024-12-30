import json
import random
from datetime import datetime, timedelta

# 무작위 데이터 생성 함수
def generate_random_data(num_records=100):
    departments = ['CS', 'HES', 'Lenovo']
    types = [0, 1]  # 0: 배송, 1: 회수
    sla_types = ['4HR', 'PO4']
    statuses = [0, 1, 2, 4]  # 대기, 진행, 완료, 이슈
    names = ['김기사', '박기사', '이기사', '정기사']
    addresses = ['서울시 강남구', '부산시 해운대구', '대구시 달서구', '인천시 계양구']
    recipients = ['홍길동', '김철수', '이영희', '박민수']
    reasons = ['주소 오류', '연락 두절', '배송 지연', '수령인 부재', None]

    data = []
    for _ in range(num_records):
        dps = random.randint(1000000000, 9999999999)
        eta = datetime.now() + timedelta(days=random.randint(1, 5), hours=random.randint(0, 23))
        depart_time = eta - timedelta(hours=random.randint(1, 3)) if random.random() > 0.3 else None
        arrive_time = eta + timedelta(hours=random.randint(1, 2)) if depart_time else None
        delivery_duration = (
            int((arrive_time - depart_time).total_seconds() // 60)
            if depart_time and arrive_time
            else None
        )

        record = {
            "department": random.choice(departments),
            "type": random.choice(types),
            "delivery": random.choice(names),
            "dps": dps,
            "sla": random.choice(sla_types),
            "eta": eta.strftime('%Y-%m-%d %H:%M'),
            "depart_time": depart_time.strftime('%Y-%m-%d %H:%M') if depart_time else None,
            "arrive_time": arrive_time.strftime('%Y-%m-%d %H:%M') if arrive_time else None,
            "delivery_duration": delivery_duration,
            "status": random.choice(statuses),
            "address": random.choice(addresses),
            "recipient": random.choice(recipients),
            "reason": random.choice(reasons)
        }
        data.append(record)

    return data

# JSON 데이터 생성 및 파일 저장
data = generate_random_data(100)
with open('delivery_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("JSON 파일 생성 완료: delivery_data.json")
