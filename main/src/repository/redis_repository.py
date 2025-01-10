# src/repository/redis_repository.py
from typing import Dict, List, Optional
import logging
import redis
import json
from src.config.base_config import RedisConfig, CacheConfig

logger = logging.getLogger(__name__)

class RedisRepository:
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
            logger.info("Redis repository initialized")

    def get_drivers(self) -> Optional[List[Dict]]:
        """기사 정보 조회"""
        try:
            data = self.client.get('master:drivers')
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting drivers from cache: {str(e)}")
            return None

    def set_drivers(self, drivers: List[Dict]) -> bool:
        """기사 정보 저장"""
        try:
            return self.client.setex(
                'master:drivers',
                self.config.driver_ttl,
                json.dumps(drivers)
            )
        except Exception as e:
            logger.error(f"Error setting drivers to cache: {str(e)}")
            return False

    def get_postal_codes(self) -> Optional[Dict]:
        """우편번호 정보 조회"""
        try:
            data = self.client.get('master:postal_codes')
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting postal codes from cache: {str(e)}")
            return None

    def set_postal_codes(self, postal_codes: Dict) -> bool:
        """우편번호 정보 저장"""
        try:
            return self.client.setex(
                'master:postal_codes',
                self.config.postal_code_ttl,
                json.dumps(postal_codes)
            )
        except Exception as e:
            logger.error(f"Error setting postal codes to cache: {str(e)}")
            return False

    def get_dashboard_data(self, key: str) -> Optional[Dict]:
        """대시보드 데이터 조회"""
        try:
            data = self.client.get(f'dashboard:{key}')
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting dashboard data from cache: {str(e)}")
            return None

    def set_dashboard_data(self, key: str, data: Dict) -> bool:
        """대시보드 데이터 저장"""
        try:
            return self.client.setex(
                f'dashboard:{key}',
                self.config.dashboard_ttl,
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Error setting dashboard data to cache: {str(e)}")
            return False