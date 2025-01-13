# src/repository/redis_repository.py
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
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            logger.info("Redis connection initialized")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def get(self, key: str) -> Optional[str]:
        """데이터 조회"""
        try:
            return self.redis_client.get(key)
        except redis.RedisError as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """데이터 저장 (기본 5분 유효)"""
        try:
            return self.redis_client.setex(key, timeout, value)
        except redis.RedisError as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """데이터 삭제"""
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> bool:
        """패턴으로 데이터 삭제"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except redis.RedisError as e:
            logger.error(f"Redis delete pattern error for {pattern}: {e}")
            return False

    def get_hash_data(self, hash_key: str) -> Dict:
        """해시 데이터 조회"""
        try:
            return self.redis_client.hgetall(hash_key)
        except redis.RedisError as e:
            logger.error(f"Redis hash get error for {hash_key}: {e}")
            return {}

    def set_hash_data(self, hash_key: str, data: Dict, timeout: int = 300) -> bool:
        """해시 데이터 저장"""
        try:
            pipeline = self.redis_client.pipeline()
            pipeline.hmset(hash_key, data)
            pipeline.expire(hash_key, timeout)
            pipeline.execute()
            return True
        except redis.RedisError as e:
            logger.error(f"Redis hash set error for {hash_key}: {e}")
            return False