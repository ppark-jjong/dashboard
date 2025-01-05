# dashboard_service.py
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import traceback
import os

from src.models.avro_redis import RedisProcessor
from src.models.avro_db import DBProcessor
from src.repository.redis_repository import RedisClient
from src.repository.mysql_repository import MySQLClient

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DashboardService:
    def __init__(self, redis_client: Optional[RedisClient] = None, mysql_client: Optional[MySQLClient] = None):
        logger.info("Initializing DashboardService")
        try:
            self.redis_client = redis_client or RedisClient()
            self.mysql_client = mysql_client or MySQLClient()

            # 현재 파일의 디렉토리 경로 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # src 디렉토리 경로 찾기
            src_dir = os.path.dirname(current_dir)
            # schemas 디렉토리 경로
            schemas_dir = os.path.join(src_dir, 'schemas')

            logger.info(f"Schemas directory path: {schemas_dir}")

            # 스키마 파일 경로 설정
            self.redis_processor = RedisProcessor(
                os.path.join(schemas_dir, 'redis_model.avsc')
            )
            self.delivery_processor = DBProcessor(
                os.path.join(schemas_dir, 'delivery_model.avsc')
            )
            self.return_processor = DBProcessor(
                os.path.join(schemas_dir, 'return_model.avsc')
            )
            self.driver_processor = DBProcessor(
                os.path.join(schemas_dir, 'driver_model.avsc')
            )
            self.postal_processor = DBProcessor(
                os.path.join(schemas_dir, 'postal_code_model.avsc')
            )

            logger.info("DashboardService initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize DashboardService: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def sync_data_to_mysql(self):
        """Redis 데이터를 MySQL로 동기화"""
        logger.info("Starting data synchronization from Redis to MySQL")

        try:
            # Redis에서 모든 배송 데이터 가져오기
            delivery_keys = await self.redis_client.get_keys("dashboard:deliveries:*")
            deliveries = [
                await self.redis_client.get_dashboard_data(key)
                for key in delivery_keys
            ]

            logger.info(f"Retrieved {len(deliveries)} deliveries from Redis")

            # Redis 데이터를 MySQL에 저장
            for delivery in deliveries:
                try:
                    # 데이터 검증 및 변환
                    if not self.delivery_processor.validate_redis_data(delivery, 'delivery'):
                        logger.warning(f"Invalid Redis delivery data: {delivery.get('dps')}")
                        continue

                    db_data = self.delivery_processor.to_db_format(delivery, 'delivery')

                    # MySQL 업데이트
                    success = await self.mysql_client.upsert_delivery(db_data)
                    if success:
                        logger.info(f"Successfully synchronized delivery: {delivery['dps']}")
                    else:
                        logger.warning(f"Failed to synchronize delivery: {delivery['dps']}")

                except Exception as e:
                    logger.error(f"Error synchronizing delivery data: {delivery.get('dps')}")
                    logger.error(f"Details: {str(e)}")
                    continue

            logger.info("Data synchronization from Redis to MySQL completed")
            return True

        except Exception as e:
            logger.error("Failed to synchronize data from Redis to MySQL")
            logger.error(f"Error details: {str(e)}")
            return False

    async def get_dashboard_data(self) -> List[Dict]:
        """대시보드 데이터 조회"""
        try:
            data = await self.redis_client.get_dashboard_data()

            # 데이터 정렬 (ETA 기준)
            sorted_data = sorted(
                data,
                key=lambda x: x.get('eta', 0) or float('inf')
            )

            return sorted_data

        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return []

    async def update_delivery_status(self, delivery_id: str, new_status: str) -> bool:
        """배송/회수 상태 업데이트"""
        try:
            # Redis 키 패턴 결정
            redis_key_patterns = [
                f"dashboard:deliveries:{delivery_id}",
                f"dashboard:returns:{delivery_id}"
            ]

            # 해당하는 키 찾기
            for key_pattern in redis_key_patterns:
                exists = await self.redis_client.check_key_exists(key_pattern)
                if exists:
                    # Redis 업데이트
                    redis_success = await self.redis_client.update_status(key_pattern, new_status)
                    if not redis_success:
                        return False

            return False

        except Exception as e:
            logger.error(f"Status update error for delivery ID {delivery_id}: {str(e)}")
            return False

    async def assign_driver(self, delivery_ids: List[str], driver_id: str) -> bool:
        """기사 할당"""
        try:
            success = True
            for delivery_id in delivery_ids:
                # Redis 키 패턴 결정
                redis_key_patterns = [
                    f"dashboard:deliveries:{delivery_id}",
                    f"dashboard:returns:{delivery_id}"
                ]

                # 해당하는 키 찾기
                for key_pattern in redis_key_patterns:
                    exists = await self.redis_client.check_key_exists(key_pattern)
                    if exists:
                        # Redis 업데이트
                        redis_success = await self.redis_client.update_driver(key_pattern, driver_id)

            return success

        except Exception as e:
            logger.error(f"Driver assignment error: {str(e)}")
            return False
