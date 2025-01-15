# generate_mock_dashboard.py

import random
import json
from datetime import datetime, timedelta
import os

# (1) 목업에 사용할 상수들
types = ["delivery", "return"]  # 테이블 ENUM('delivery','return')에 맞춤
statuses = ["대기", "진행", "완료", "이슈"]
districts = [
    "강남구", "강동구", "강서구", "강북구", "관악구",
    "광진구", "구로구", "금천구", "노원구", "도봉구"
]
warehouses = ["물류센터A", "물류센터B", "물류센터C"]
departments = ["CS팀", "HES팀"]
cities = ["서울시", "경기도", "인천시"]
sla_types = ["4HR", "P04", "P24", "STD", "EXP", "VIP"]

# (2) 포매팅 함수
def format_date(dt):
    # 예) 2025-01-15 09:30
    return dt.strftime("%Y-%m-%d %H:%M")

def generate_postal_code():
    # 5자리 우편번호 생성 (10000 ~ 99999)
    return str(random.randint(10000, 99999))

def generate_phone_number():
    # 예) 010-1234-5678 형식
    return f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}"

# (3) 100개의 대시보드용 Mock 데이터 생성
dashboard_data = []
now = datetime.now()

for i in range(1, 101):  # 1부터 100까지
    row_id = i  # AUTO_INCREMENT PK 대용

    # 랜덤 선택
    pick_type = random.choice(types)
    pick_status = random.choice(statuses)
    city = random.choice(cities)
    district = random.choice(districts)
    postal_code = generate_postal_code()
    department = random.choice(departments)
    warehouse = random.choice(warehouses)
    sla = random.choice(sla_types)

    # region = city + ' ' + district
    region = f"{city} {district}"

    # 대략 현재 시각을 기준으로 ±12시간 내외
    base_time = now + timedelta(hours=random.randint(-12, 12))

    # driver 정보 (대기 상태라면 None)
    driver_id = None
    driver_name = ""
    driver_contact = ""

    if pick_status != "대기":
        # 드라이버는 10명 정도 있다고 가정
        driver_id = random.randint(1, 10)
        driver_name = f"김기사{driver_id}"
        driver_contact = generate_phone_number()

    # depart_time (대기 상태면 null)
    depart_time = base_time if pick_status != "대기" else None

    # eta (depart_time 이후 1~3시간 사이로 가정)
    eta_time = None
    if depart_time:
        eta_time = depart_time + timedelta(hours=random.uniform(1, 3))

    # duration_time (30~150분 사이)
    duration_time = random.randint(30, 150)

    # completed_time (완료 상태면 depart_time + duration_time)
    completed_time = None
    if pick_status == "완료" and depart_time:
        completed_time = depart_time + timedelta(minutes=duration_time)

    # remark (30% 확률로 특이사항 있음)
    remark = "특이사항 있음" if random.random() < 0.3 else ""

    # (4) JSON 객체 구성
    data_row = {
        "id": row_id,
        "type": pick_type,  # delivery or return
        "status": pick_status,
        "driver_id": driver_id,
        "driver_name": driver_name,
        "driver_contact": driver_contact,
        "department": department,
        "postal_code": postal_code,
        "region": region,
        "duration_time": duration_time,  # 분
        "address": f"{city} {district} 테스트길 {random.randint(1,100)}번",
        "customer": f"고객{random.randint(1,100)}",
        "contact": generate_phone_number(),
        "remark": remark,
        "eta": format_date(eta_time) if eta_time else None,
        "depart_time": format_date(depart_time) if depart_time else None,
        "completed_time": format_date(completed_time) if completed_time else None,
        "sla": sla,
        "warehouse": warehouse,
        "dps": "9545" + "".join(str(random.randint(0, 9)) for _ in range(6))
    }

    dashboard_data.append(data_row)

base_dir = r"C:\\MyMain\\dashboard\\main\\main_project\\back\\mock"
file_name = "dashboard_mock.json"
save_path = os.path.join(base_dir, file_name)

# (6) 파일로 쓰기 (ensure_ascii=False로 한글 깨짐 방지)
with open(save_path, "w", encoding="utf-8") as f:
    json.dump(dashboard_data, f, indent=2, ensure_ascii=False)

# (7) 경로를 로그로 확인
print(f"JSON 파일이 생성되었습니다: {save_path}")
