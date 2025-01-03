import redis
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from dotenv import load_dotenv

from ..config.main_config import RedisConfig


class RedisClient:
    def __init__(self, config: Optional[RedisConfig] = None):
        self.config = config or RedisConfig()
        self.redis = redis.Redis(**self.config.to_dict())

    async def set_dashboard_data(self, key: str, data: Dict) -> bool:
        """대시보드 데이터 저장"""
        try:
            # None 값을 빈 문자열로 변환
            cleaned_data = {
                k: str(v) if v is not None else ''
                for k, v in data.items()
            }

            # Redis hash로 저장
            self.redis.hmset(key, cleaned_data)
            return True
        except Exception as e:
            print(f"Redis set data error: {e}")
            return False

    async def get_dashboard_data(self) -> List[Dict[str, Any]]:
        """대시보드 데이터 조회"""
        try:
            # dashboard:deliveries:* 와 dashboard:returns:* 패턴의 모든 키 조회
            all_keys = self.redis.keys("dashboard:*")

            data = []
            for key in all_keys:
                item_data = self.redis.hgetall(key)
                if item_data:
                    # 바이트 데이터를 문자열로 디코딩
                    decoded_data = {
                        k.decode('utf-8'): v.decode('utf-8')
                        for k, v in item_data.items()
                    }

                    # 빈 문자열을 None으로 변환
                    processed_data = {
                        k: None if v == '' else v
                        for k, v in decoded_data.items()
                    }

                    # 타임스탬프 필드 처리
                    for field in ['depart_time', 'completed_time', 'eta']:
                        if processed_data.get(field):
                            try:
                                processed_data[field] = int(processed_data[field])
                            except (ValueError, TypeError):
                                processed_data[field] = None

                    data.append(processed_data)

            return data

        except Exception as e:
            print(f"Redis get data error: {e}")
            return []

    async def check_key_exists(self, key: str) -> bool:
        """Redis 키 존재 여부 확인"""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            print(f"Redis key check error: {e}")
            return False

    async def update_status(self, key: str, status: str) -> bool:
        """상태 업데이트"""
        try:
            self.redis.hset(key, 'status', status)
            self.redis.hset(key, 'last_updated', datetime.now().isoformat())
            return True
        except Exception as e:
            print(f"Redis status update error: {e}")
            return False

    async def update_driver(self, key: str, driver_id: str) -> bool:
        """기사 할당 정보 업데이트"""
        try:
            self.redis.hset(key, 'driver', driver_id)
            self.redis.hset(key, 'last_updated', datetime.now().isoformat())
            return True
        except Exception as e:
            print(f"Redis driver assignment error: {e}")
            return False

    async def is_connected(self) -> bool:
        """Redis 연결 상태 확인"""
        try:
            return bool(self.redis.ping())
        except Exception:
            return False