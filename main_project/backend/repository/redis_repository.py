from sqlalchemy.orm import Session
import aioredis
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
import logging

logger = logging.getLogger(__name__)


class RedisRepository:
    def __init__(self, redis):
        self.redis = redis

    def _serialize_datetime(self, data: dict) -> dict:
        """datetime 및 date 필드 직렬화 공통 유틸리티"""
        serialized = data.copy()
        datetime_fields = [
            "eta",
            "dispatch_date",
            "depart_time",
            "completed_time",
            "dispatch_time",
        ]

        for field in datetime_fields:
            if serialized.get(field):
                if isinstance(serialized[field], datetime):
                    serialized[field] = serialized[field].isoformat()
                elif isinstance(serialized[field], date):
                    serialized[field] = serialized[field].isoformat()

        return serialized

    async def get_by_dps(self, dps: str) -> Optional[Dict[str, Any]]:
        """DPS로 데이터 조회"""
        data = await self.redis.get(f"dashboard:{dps}")
        return json.loads(data) if data else None

    async def save_task(self, task_type: str, task: dict) -> bool:
        """작업 데이터 Redis 저장"""
        try:
            # datetime 필드 직렬화
            data = self._serialize_datetime(task)

            # Redis 키 생성
            key = f"dashboard:{data['dps']}"

            logger.info(f"Saving to Redis - Key: {key}")

            # JSON으로 직렬화하여 저장 (날짜/시간 처리 포함)
            await self.redis.set(key, json.dumps(data, default=str))
            return True

        except Exception as e:
            logger.error(f"Error saving task to Redis: {e}")
            return False

    async def get_all(self):
        try:
            keys = await self.redis.keys("dashboard:*")
            if not keys:
                return []

            data = await self.redis.mget(keys)
            return [json.loads(item) for item in data if item]
        except Exception as e:
            logger.error(f"Error getting data from Redis: {e}")
            return []

    async def clear_all(self) -> bool:
        """모든 dashboard 데이터 삭제"""
        try:
            keys = await self.redis.keys("dashboard:*")
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception as e:
            print(f"Error clearing Redis data: {e}")
            return False
