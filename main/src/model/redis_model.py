import redis

# Redis 클라이언트 초기화
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)


def validate_record(record):
    if not isinstance(record, dict):
        raise ValueError(f"Record is not a dictionary: {record}")
    for key, value in record.items():
        if not isinstance(key, str):
            raise ValueError(f"Key {key} is not a string.")
        if value is not None and not isinstance(value, (str, int, float)):
            raise ValueError(f"Value {value} for key {key} is not a valid Redis type.")


def sanitize_record(record):
    return {k: (str(v) if v is not None else "") for k, v in record.items()}


data = [
    {'department': 'Lenovo', 'type': 0, 'delivery': '박기사', 'dps': 8736667602, 'sla': '4HR', 'eta': '2024-12-28 00:18',
     'depart_time': '2024-12-27 23:18', 'arrive_time': '2024-12-28 01:18', 'delivery_duration': 120, 'status': 4,
     'address': '인천시 계양구', 'recipient': '홍길동', 'reason': '주소 오류'}
]


def inspect_redis_key(key):
    print(f"Inspecting key: {key}")
    data = redis_client.hgetall(key)
    print(f"Data in Redis: {data}")


for record in data:
    try:
        validate_record(record)
        sanitized_record = sanitize_record(record)

        print(f"Sanitized Record: {sanitized_record}")
        key = f"delivery:{sanitized_record['dps']}"
        print(f"Redis Key: {key}")

        # hset으로 변경 (Redis 4.0.0 이상)
        redis_client.delete(key)  # 기존 키 삭제
        for field, value in sanitized_record.items():
            redis_client.hset(key, field, value)

        print(f"Record {sanitized_record['dps']} successfully inserted.")
    except Exception as e:
        print(f"Error processing record {record}: {e}")

    inspect_redis_key(key)

print(f"Record Types: { {k: type(v) for k, v in sanitized_record.items()} }")