import redis
import pandas as pd

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

def get_delivery_data():
    raw_data = redis_client.get("delivery_data")  # Redis 키에서 데이터 가져오기
    if raw_data:
        return pd.read_json(raw_data)
    return pd.DataFrame()  # 빈 DataFrame 반환

def get_driver_data():
    raw_data = redis_client.get("driver_data")
    if raw_data:
        return pd.read_json(raw_data)
    return pd.DataFrame()
