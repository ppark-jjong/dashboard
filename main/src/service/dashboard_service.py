# src/service/dashboard_service.py
from typing import Optional, Dict
from datetime import datetime
import json
import logging
from sqlalchemy.exc import SQLAlchemyError

from src.repository.mysql_repository import MySQLRepository
from src.repository.redis_repository import RedisRepository
from src.schema.main_dto import (
    FilterParams, StatusUpdateRequest, DriverAssignRequest,
    DashboardDataResponse, StatusUpdateResponse, DriversListResponse,
    DriverAssignResponse
)

logger = logging.getLogger(__name__)


class DashboardService:
    def __init__(self, mysql_repo: Optional[MySQLRepository] = None, redis_repo: Optional[RedisRepository] = None):
        """서비스 초기화"""
        self.mysql_repo = mysql_repo or MySQLRepository()
        self.redis_repo = redis_repo or RedisRepository()

    def refresh_dashboard(self) -> bool:
        """대시보드 데이터 새로고침"""
        try:
            logger.info("Starting dashboard refresh...")
            success = self.mysql_repo.sync_dashboard_data()

            if success:
                self.redis_repo.delete_pattern("dashboard:*")
                logger.info("Dashboard refresh completed successfully")

            return success

        except SQLAlchemyError as e:
            logger.error(f"Database error during refresh: {e}")
            raise
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
            raise

    def get_dashboard_data(self, filters: FilterParams) -> DashboardDataResponse:
        """대시보드 데이터 조회"""
        try:
            cache_key = f"dashboard:list:{hash(frozenset(filters.dict().items()))}"

            cached_data = self.redis_repo.get(cache_key)
            if cached_data:
                return DashboardDataResponse.parse_raw(cached_data)

            skip = (filters.page - 1) * filters.page_size
            items, total = self.mysql_repo.get_dashboard_items(
                skip=skip,
                limit=filters.page_size,
                filters=filters.dict(exclude_none=True)
            )

            formatted_items = [{
                'department': item.department,
                'type': item.type,
                'warehouse': item.warehouse or '-',
                'driver_name': item.driver_name or '-',
                'dps': item.dps,
                'sla': item.sla or '-',
                'eta': item.eta.strftime("%Y-%m-%d %H:%M") if item.eta else '-',
                'status': item.status,
                'district': item.district or '-',
                'duration_time': f"{item.duration_time}분" if item.duration_time else '-'
            } for item in items]

            response = DashboardDataResponse(
                data=formatted_items,
                total_records=total,
                total_pages=(total + filters.page_size - 1) // filters.page_size,
                current_page=filters.page,
                page_size=filters.page_size
            )

            self.redis_repo.set(cache_key, response.json())
            return response

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise

    def get_detail_data(self, dps: str) -> Dict:
        """상세 정보 조회"""
        try:
            cache_key = f"dashboard:detail:{dps}"

            cached_data = self.redis_repo.get(cache_key)
            if cached_data:
                return json.loads(cached_data)

            detail_data = self.mysql_repo.get_dashboard_detail(dps)
            if not detail_data:
                raise ValueError(f"No dashboard item found with DPS: {dps}")

            formatted_data = {
                **detail_data,
                'eta': detail_data['eta'].strftime("%Y-%m-%d %H:%M") if detail_data['eta'] else '-',
                'depart_time': detail_data['depart_time'].strftime("%Y-%m-%d %H:%M") if detail_data[
                    'depart_time'] else '-',
                'completed_time': detail_data['completed_time'].strftime("%Y-%m-%d %H:%M") if detail_data[
                    'completed_time'] else '-',
                'duration_time': f"{detail_data['duration_time']}분" if detail_data['duration_time'] else '-'
            }

            self.redis_repo.set(cache_key, json.dumps(formatted_data))
            return formatted_data

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting detail data: {e}")
            raise

    def update_status(self, dps: str, new_status: str) -> StatusUpdateResponse:
        """상태 업데이트"""
        try:
            current_data = self.mysql_repo.get_dashboard_detail(dps)
            if not current_data:
                raise ValueError(f"No item found with DPS: {dps}")

            valid_transitions = {
                '대기': ['진행'],
                '진행': ['완료', '이슈'],
                '완료': [],
                '이슈': ['진행']
            }

            current_status = current_data['status']
            if new_status not in valid_transitions.get(current_status, []):
                raise ValueError(f"Invalid status transition from {current_status} to {new_status}")

            success = self.mysql_repo.update_dashboard_status(dps, new_status)
            if success:
                self.redis_repo.delete_pattern("dashboard:*")
                return StatusUpdateResponse(
                    message="Status updated successfully",
                    delivery_id=dps,
                    updated_status=new_status
                )

            raise ValueError(f"Failed to update status for DPS: {dps}")

        except Exception as e:
            logger.error(f"Error updating status: {e}")
            raise

    def assign_driver(self, dps_list: list[str], driver_id: int) -> DriverAssignResponse:
        """기사 할당"""
        try:
            success = self.mysql_repo.assign_driver(dps_list, driver_id)
            if success:
                self.redis_repo.delete_pattern("dashboard:*")
                return DriverAssignResponse(
                    message="Driver assigned successfully",
                    assigned_count=len(dps_list),
                    driver_id=driver_id
                )

            raise ValueError(f"Failed to assign driver {driver_id}")

        except Exception as e:
            logger.error(f"Error assigning driver: {e}")
            raise

    def get_drivers(self) -> DriversListResponse:
        """기사 목록 조회"""
        try:
            cache_key = "dashboard:drivers"

            cached_data = self.redis_repo.get(cache_key)
            if cached_data:
                return DriversListResponse.parse_raw(cached_data)

            drivers = self.mysql_repo.get_drivers()
            response = DriversListResponse(
                drivers=drivers,
                message="Drivers retrieved successfully"
            )

            self.redis_repo.set(cache_key, response.json())
            return response

        except Exception as e:
            logger.error(f"Error getting drivers: {e}")
            raise