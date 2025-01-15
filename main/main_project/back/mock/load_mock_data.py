# load_mock_data.py
import json
import logging
from pathlib import Path
from back.repository.redis_repository import RedisRepository

logger = logging.getLogger(__name__)

def load_mock_data_to_redis():
    """
    mock.json 파일을 읽어서 Redis에 key-value 형태로 저장.
    예: key='dashboard:<id>' / value=json.dumps(item)
    """
    repo = RedisRepository()

    mock_file = Path("./mock.json")  # mock.json 경로
    if not mock_file.exists():
        logger.error(f"Mock file not found: {mock_file.resolve()}")
        return
    
    with mock_file.open("r", encoding="utf-8") as f:
        data_list = json.load(f)

    if not isinstance(data_list, list):
        logger.error("mock.json 데이터가 리스트 형태가 아닙니다.")
        return
    
    # 예: dashboard:<id> 형식으로 저장
    for item in data_list:
        item_id = item.get("id")
        if item_id is None:
            logger.warning(f"Item has no 'id' field: {item}")
            continue

        key = f"dashboard:{item_id}"
        value_str = json.dumps(item, ensure_ascii=False)

        repo.redis_client.set(key, value_str)
        logger.info(f"Saved to Redis -> key={key}, value={item}")

    logger.info("Mock data loading to Redis completed.")

if __name__ == "__main__":
    # 스크립트 단독 실행 시, mock.json -> Redis 적재
    logging.basicConfig
