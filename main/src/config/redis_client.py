import redis
import json
from typing import Dict, List, Any
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=True
        )
        # Dashboard 관련 키
        self.dashboard_key = "dashboard:deliveries"
        self.dashboard_status_key = "dashboard:status"
        self.last_sync_key = "dashboard:last_sync"
        self.driver_assignments_key = "dashboard:driver_assignments"

    def cache_dashboard_data(self, data: List[Dict[str, Any]]) -> None:
        """대시보드 데이터를 캐시에 저장"""
        pipeline = self.redis.pipeline()

        # 기존 데이터 삭제
        pipeline.delete(self.dashboard_key)

        # 새 데이터 저장
        for item in data:
            # DPS를 키로 사용
            item_key = f"{self.dashboard_key}:{item['dps']}"
            pipeline.hset(item_key, mapping={
                'dashboard_id': item['dashboard_id'],
                'department': item['department'],
                'type': item['type'],
                'status': item.get('status', 'WAITING'),
                'driver': str(item.get('driver', '')),
                'last_updated': datetime.now().isoformat()
            })

        # 마지막 동기화 시간 업데이트
        pipeline.set(self.last_sync_key, datetime.now().isoformat())

        # 모든 작업 실행
        pipeline.execute()

    def get_dashboard_data(self) -> List[Dict[str, Any]]:
        """캐시된 대시보드 데이터 조회"""
        # dashboard:deliveries:* 패턴의 모든 키 조회
        keys = self.redis.keys(f"{self.dashboard_key}:*")

        data = []
        for key in keys:
            item_data = self.redis.hgetall(key)
            if item_data:  # 데이터가 있는 경우만 추가
                # DPS 추출 (키에서 마지막 부분)
                dps = key.split(":")[-1]
                item_data['dps'] = dps
                data.append(item_data)

        return data

    def update_delivery_status(self, dps: str, status: str) -> bool:
        """배송 상태 업데이트"""
        key = f"{self.dashboard_key}:{dps}"
        try:
            self.redis.hset(key, 'status', status)
            self.redis.hset(key, 'last_updated', datetime.now().isoformat())
            return True
        except Exception as e:
            print(f"Redis update error: {e}")
            return False

    def assign_driver(self, dps: str, driver_id: str) -> bool:
        """기사 할당 정보 업데이트"""
        key = f"{self.dashboard_key}:{dps}"
        try:
            self.redis.hset(key, 'driver', driver_id)
            self.redis.hset(key, 'last_updated', datetime.now().isoformat())
            return True
        except Exception as e:
            print(f"Redis driver assignment error: {e}")
            return False

    def get_last_sync_time(self) -> str:
        """마지막 동기화 시간 조회"""
        return self.redis.get(self.last_sync_key)

    def clear_cache(self) -> None:
        """캐시 초기화"""
        keys = self.redis.keys(f"{self.dashboard_key}:*")
        if keys:
            self.redis.delete(*keys)
        self.redis.delete(self.last_sync_key)

    def is_connected(self) -> bool:
        """Redis 연결 상태 확인"""
        try:
            return bool(self.redis.ping())
        except Exception:
            return False