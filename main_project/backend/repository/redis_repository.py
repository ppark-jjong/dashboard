
#backend/repository/redis_repository.py
import redis
import json
from datetime import datetime
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)

class RedisRepository:
    def __init__(self):
        """Redis 연결 초기화"""
        try:
            self.redis_client = redis.Redis(
                host='redis',
                port=6379,
                decode_responses=True
            )
            logger.info("Redis connection initialized")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
        
    def set_data(self, key: str, value: str):
        """데이터를 Redis에 저장"""
        try:
            self.redis_client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Error saving to Redis: {e}")
            return False

    def get_data(self, key: str) -> Optional[str]:
        """Redis에서 데이터 조회"""
        try:
            return self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Error getting data from Redis: {e}")
            return None