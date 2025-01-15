# back/repository/redis_repository.py
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
