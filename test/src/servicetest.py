import os
import json
import redis
import logging

# Redis 설정
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# 데이터 파일 경로 리스트
data_files = [
    "../data/data1.json",
    "../data/data2.json",
    "../data/data3.json",
    "../data/data4.json",
    "../data/data5.json"
]

# 현재 데이터 파일 인덱스
current_index = 0


def fetch_data(file_path):
    """주어진 경로에서 JSON 데이터를 로드"""
    if not os.path.exists(file_path):
        logging.error(f"파일을 찾을 수 없습니다: {file_path}")
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logging.info(f"파일을 성공적으로 로드했습니다: {file_path}")
            return data
    except Exception as e:
        logging.error(f"파일 로드 중 오류 발생: {file_path} - {str(e)}")
        return None


def sanitize_record(record):
    """레코드에서 None 값을 빈 문자열로 변환"""
    return {k: (v if v is not None else "") for k, v in record.items()}


def insert_data_to_redis():
    """현재 인덱스의 데이터 파일을 Redis에 삽입"""
    global current_index
    file_path = data_files[current_index]
    data = fetch_data(file_path)
    if not data:
        logging.warning(f"데이터가 비어 있거나 로드에 실패했습니다: {file_path}")
        return

    for record in data:
        key = f"delivery:{record['DPS']}"
        try:
            sanitized_record = sanitize_record(record)
            for field, value in sanitized_record.items():
                redis_client.hset(key, field, value)
            logging.info(f"Redis에 데이터 저장 완료 - Key: {key}")
        except Exception as e:
            logging.error(f"Redis 데이터 삽입 중 오류 발생: {e}")

    current_index = (current_index + 1) % len(data_files)
    logging.info(f"다음에 사용할 데이터 파일 인덱스: {current_index}")


def get_redis_data():
    """Redis에서 모든 데이터를 조회"""
    try:
        keys = redis_client.keys("delivery:*")
        data = []
        for key in keys:
            record = redis_client.hgetall(key)
            if record:
                data.append(record)
        logging.info(f"Redis에서 {len(data)}개의 데이터를 성공적으로 조회했습니다.")
        return data
    except Exception as e:
        logging.error(f"Redis 데이터 조회 중 오류 발생: {e}")
        return []
