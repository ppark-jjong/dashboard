# src/service/dashboard_service.py
from typing import Dict, List, Any
from datetime import datetime
import logging
from src.repository.mysql_repository import MySQLRepository
from src.repository.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class DashboardService:
    def __init__(self, mysql_repo=None, cache_repo=None):
        self.mysql_repo = MySQLRepository()
        self.cache_repo = RedisRepository()

    def get_dashboard_data(self, page: int = 1, page_size: int = 15, filters: Dict = None) -> Dict[str, Any]:
        """대시보드 데이터 조회 with 필터링"""
        logger.info(f"Getting dashboard data with filters: {filters}")
        try:
            # 필터 전처리
            processed_filters = {}
            if filters:
                logger.info("Processing filters...")
                if 'department' in filters:
                    processed_filters['department'] = filters['department']
                    logger.info(f"Applied department filter: {filters['department']}")

                if 'status' in filters:
                    processed_filters['status'] = filters['status']
                    logger.info(f"Applied status filter: {filters['status']}")

                if 'driver' in filters:
                    processed_filters['driver'] = filters['driver']
                    logger.info(f"Applied driver filter: {filters['driver']}")

                if 'search' in filters and filters['search']:
                    processed_filters['search'] = filters['search']
                    logger.info(f"Applied search filter: {filters['search']}")

            # 리포지토리에서 데이터 조회
            raw_data = self.repository.get_dashboard_data(
                page=page,
                page_size=page_size,
                filters=processed_filters
            )
            logger.debug(f"Retrieved raw data: {raw_data}")

            # 데이터 포맷팅
            formatted_data = []
            for item in raw_data.get('data', []):
                formatted_item = self.format_dashboard_data(item)
                formatted_data.append(formatted_item)

            result = {
                'data': formatted_data,
                'total_records': raw_data.get('total_records', 0),
                'page': raw_data.get('page', 1),
                'page_size': raw_data.get('page_size', 15),
                'total_pages': raw_data.get('total_pages', 1)
            }

            logger.info(f"Returning {len(formatted_data)} records")
            return result

        except Exception as e:
            logger.error(f"Error processing dashboard data: {str(e)}")
            raise

    def format_dashboard_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 포맷팅"""
        try:
            formatted = {
                'department': data.get('department', '-'),
                'type': '배송' if data.get('type') == 'delivery' else '회수',
                'warehouse': data.get('warehouse', '-'),
                'driver_name': data.get('driver_name', '-'),
                'dps': data.get('dps', '-'),
                'sla': data.get('sla', '-'),
                'eta': data['eta'].strftime('%Y-%m-%d %H:%M') if data.get('eta') else '-',
                'status': data.get('status', '-'),
                'district': data.get('district', '-'),
                'contact': data.get('contact', '-'),
                'address': data.get('address', '-'),
                'customer': data.get('customer', '-'),
                'remark': data.get('remark', '-'),
                'depart_time': data['depart_time'].strftime('%Y-%m-%d %H:%M') if data.get('depart_time') else '-',
                'duration_time': f"{data.get('duration_time', 0)}분"
            }
            return formatted
        except Exception as e:
            logger.error(f"Error formatting data: {str(e)}")
            raise

    def update_delivery_status(self, delivery_id: str, new_status: str) -> bool:
        """배송 상태 업데이트"""
        logger.info(f"Updating delivery status - ID: {delivery_id}, New status: {new_status}")
        try:
            if not delivery_id or not new_status:
                logger.error("Invalid delivery_id or status")
                return False

            if new_status not in ['대기', '진행', '완료', '취소']:
                logger.error(f"Invalid status value: {new_status}")
                return False

            result = self.repository.update_delivery_status(delivery_id, new_status)
            logger.info(f"Status update {'successful' if result else 'failed'}")
            return result
        except Exception as e:
            logger.error(f"Error updating delivery status: {str(e)}")
            return False

    def assign_driver(self, delivery_ids: List[str], driver_id: str) -> bool:
        """기사 할당"""
        logger.info(f"Assigning driver {driver_id} to deliveries: {delivery_ids}")
        try:
            if not delivery_ids or not driver_id:
                logger.error("Invalid delivery_ids or driver_id")
                return False

            result = self.repository.assign_driver(delivery_ids, driver_id)
            logger.info(f"Driver assignment {'successful' if result else 'failed'}")
            return result
        except Exception as e:
            logger.error(f"Error assigning driver: {str(e)}")
            return False

    def get_drivers(self) -> List[Dict]:
        """기사 목록 조회 with Redis 캐시"""
        try:
            # Redis에서 조회
            cached_drivers = self.redis_repo.get_drivers()
            if cached_drivers:
                return cached_drivers

            # MySQL에서 조회
            drivers = self.mysql_repo.get_drivers()
            if drivers:
                # Redis에 캐시
                self.redis_repo.set_drivers(drivers)
            return drivers

        except Exception as e:
            logger.error(f"Error getting drivers: {str(e)}")
            return []

    def filter_data(self, data: List[Dict], **filters) -> List[Dict]:
        """데이터 필터링"""
        logger.info(f"Filtering data with: {filters}")
        try:
            filtered = data.copy()

            if filters.get('department') and filters['department'] != 'all':
                filtered = [d for d in filtered if d['department'] == filters['department']]

            if filters.get('status') and filters['status'] != 'all':
                filtered = [d for d in filtered if d['status'] == filters['status']]

            if filters.get('driver') and filters['driver'] != 'all':
                filtered = [d for d in filtered if d['driver_name'] == filters['driver']]

            if filters.get('search'):
                search_term = filters['search'].lower()
                filtered = [d for d in filtered if
                            search_term in str(d.get('dps', '')).lower() or
                            search_term in str(d.get('customer', '')).lower()]

            logger.info(f"Filtered {len(data)} records to {len(filtered)}")
            return filtered
        except Exception as e:
            logger.error(f"Error filtering data: {str(e)}")
            return data
