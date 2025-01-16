
# backend/repository/load_mock_data.py
import json
import logging
from pathlib import Path
from .redis_repository import RedisRepository

logger = logging.getLogger(__name__)

def load_mock_data_to_redis():
    """mock.json 파일을 읽어서 Redis에 저장"""
    repo = RedisRepository()
    
    try:
        # mock.json 파일 경로 확인
        mock_file = Path(__file__).parent / "./mock.json"  
        logger.info(f"Looking for mock.json at: {mock_file.resolve()}")

        if not mock_file.exists():
            logger.error(f"Mock file not found: {mock_file.resolve()}")
            return False

        # 파일 읽기
        with mock_file.open("r", encoding="utf-8") as f:
            data_list = json.load(f)

        if not isinstance(data_list, list):
            logger.error("mock.json 데이터가 리스트 형태가 아닙니다.")
            return False

        logger.info(f"Loaded {len(data_list)} records from mock.json")

        # Redis에 데이터 저장
        success_count = 0
        for idx, item in enumerate(data_list, start=1):
            key = f"dashboard:{idx}"  # id 값이 없으면 인덱스를 사용
            value = json.dumps(item, ensure_ascii=False)
            
            if repo.set_data(key, value):
                success_count += 1
                logger.debug(f"Saved to Redis: {key}")

        logger.info(f"Completed: {success_count}/{len(data_list)} items saved to Redis")
        return True

    except Exception as e:
        logger.error(f"Error in load_mock_data_to_redis: {e}")
        return False

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # 데이터 로드 실행
    success = load_mock_data_to_redis()
    if success:
        print("Mock data successfully loaded to Redis")
    else:
        print("Failed to load mock data to Redis")