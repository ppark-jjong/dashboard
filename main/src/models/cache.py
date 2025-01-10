# src/model/cache.py
import redis
import json
import logging
from typing import Any, Optional
from src.config.base_config import RedisConfig, CacheConfig

logger = logging.getLogger(__name__)

class CacheModel:
    """캐시 관리 모델"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'client'):
            redis_config = RedisConfig()
            self.client = redis.Redis(
                host=redis_config.host,
                port=redis_config.port,
                db=redis_config.db,
                password=redis_config.password,
                decode_responses=True
            )
            self.config = CacheConfig()
            logger.info("Cache model initialized")

    def get(self, key: str) -> Optional[Any]:
        """캐시 데이터 조회"""
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """캐시 데이터 저장"""
        try:
            serialized = json.dumps(value)
            if ttl:
                return self.client.setex(key, ttl, serialized)
            return self.client.set(key, serialized)
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """캐시 데이터 삭제"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False

    # 마스터 데이터 캐시 메서드
    def get_drivers(self) -> Optional[list]:
        return self.get('master:drivers')

    def set_drivers(self, drivers: list) -> bool:
        return self.set('master:drivers', drivers, self.config.driver_ttl)

    def get_postal_codes(self) -> Optional[dict]:
        return self.get('master:postal_codes')

    def set_postal_codes(self, postal_codes: dict) -> bool:
        return self.set('master:postal_codes', postal_codes, self.config.postal_code_ttl)