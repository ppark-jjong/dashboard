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
        """
        DashboardService 초기화
        """
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

    async def sync_data(self):
        """Redis와 MySQL 데이터 동기화"""
        logger.info("Starting data synchronization")
        try:
            # MySQL에서 데이터 조회
            logger.info("Fetching data from MySQL")
            deliveries = await self.mysql_client.get_deliveries()
            returns = await self.mysql_client.get_returns()
            logger.info(f"Retrieved {len(deliveries)} deliveries and {len(returns)} returns from MySQL")

            # 배송 데이터 동기화
            for delivery in deliveries:
                try:
                    # 배송 데이터 검증 및 변환
                    if self.delivery_processor.validate_db_data(delivery, 'delivery'):
                        avro_data = self.delivery_processor.from_db_format(delivery, 'delivery')
                        redis_data = self.redis_processor.to_redis_hash(avro_data)
                        redis_key = f"dashboard:deliveries:{delivery['dps']}"
                        success = await self.redis_client.set_dashboard_data(redis_key, redis_data)
                        if success:
                            logger.debug(f"Successfully synced delivery data. DPS: {delivery['dps']}")
                        else:
                            logger.warning(f"Failed to sync delivery data. DPS: {delivery['dps']}")
                    else:
                        logger.warning(f"Invalid delivery data format. DPS: {delivery.get('dps')}")
                except Exception as e:
                    logger.error(f"Error syncing delivery data. DPS: {delivery.get('dps')}")
                    logger.error(f"Error details: {str(e)}")
                    continue

            # 회수 데이터 동기화
            for return_data in returns:
                try:
                    # 회수 데이터 검증 및 변환
                    if self.return_processor.validate_db_data(return_data, 'return'):
                        avro_data = self.return_processor.from_db_format(return_data, 'return')
                        redis_data = self.redis_processor.to_redis_hash(avro_data)
                        redis_key = f"dashboard:returns:{return_data['dps']}"
                        success = await self.redis_client.set_dashboard_data(redis_key, redis_data)
                        if success:
                            logger.debug(f"Successfully synced return data. DPS: {return_data['dps']}")
                        else:
                            logger.warning(f"Failed to sync return data. DPS: {return_data['dps']}")
                    else:
                        logger.warning(f"Invalid return data format. DPS: {return_data.get('dps')}")
                except Exception as e:
                    logger.error(f"Error syncing return data. DPS: {return_data.get('dps')}")
                    logger.error(f"Error details: {str(e)}")
                    continue

            logger.info("Data synchronization completed successfully")
            return True

        except Exception as e:
            logger.error("Failed to complete data synchronization")
            logger.error(f"Error details: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
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
