from sqlalchemy.orm import Session
import aioredis
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
import logging

logger = logging.getLogger(__name__)


class RedisRepository:
    def __init__(self, redis):

        if redis is None:
            logger.error("RedisRepository에 None 객체가 전달되었습니다.")
            raise ValueError("유효한 Redis 연결 객체가 필요합니다.")

        logger.info(f"RedisRepository 초기화. Redis 객체: {redis}")
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
        try:
            if self.redis is None:
                logger.error("Redis 연결이 None입니다.")
                return False

            # datetime 필드 직렬화
            data = self._serialize_datetime(task)

            # Redis 키 생성
            key = f"dashboard:{data['dps']}"

            logger.info(f"Saving to Redis - Key: {key}")

            # JSON으로 직렬화하여 저장
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

    def get_dashboard(self, dashboard_id):
        # Redis에서 대시보드 데이터를 조회합니다
        try:
            data = self.redis_client.get(f"dashboard:{dashboard_id}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            # Redis 조회 실패 로그
            print(f"Redis 조회 실패: {e}")
            return None

    def cache_dashboard(self, dashboard_id, data):
        """Redis에 대시보드 데이터를 캐싱합니다."""
        try:
            self.redis_client.set(f"dashboard:{dashboard_id}", json.dumps(data))
        except Exception as e:
            print(f"Redis 캐싱 실패: {e}")
