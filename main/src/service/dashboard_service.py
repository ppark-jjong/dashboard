# src/service/dashboard_service.py
from typing import Dict, List, Any
import logging
from src.repository.mysql_repository import MySQLRepository

logger = logging.getLogger(__name__)


class DashboardService:
    def __init__(self, repository: MySQLRepository = None):
        self.repository = repository or MySQLRepository()

    def format_dashboard_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # 테이블용 기본 데이터
        table_data = {
            'department': data['department'],
            'type': '배송' if data['type'] == 'delivery' else '회수',
            'warehouse': data['warehouse'],
            'driver_name': data['driver_name'],
            'dps': data['dps'],
            'sla': data['sla'],
            'eta': data['eta'].strftime('%Y-%m-%d %H:%M') if data['eta'] else '-',
            'status': data['status'],
            'district': data['district'],
            'contact': data['contact']
        }

        # 모달용 상세 데이터
        detail_data = {
            **table_data,
            'address': data['address'],
            'customer': data['customer'],
            'remark': data['remark'],
            'depart_time': data['depart_time'].strftime('%Y-%m-%d %H:%M') if data['depart_time'] else '-',
            'duration_time': data['duration_time']
        }

        return {
            'table_data': table_data,
            'detail_data': detail_data
        }

    def get_dashboard_data(self) -> Dict[str, List[Dict[str, Any]]]:
        raw_data = self.repository.get_dashboard_data()
        formatted_data = [self.format_dashboard_data(item) for item in raw_data]

        return {
            'table_data': [item['table_data'] for item in formatted_data],
            'detail_data': {item['table_data']['dps']: item['detail_data'] for item in formatted_data}
        }

    def update_delivery_status(self, delivery_id: str, new_status: str) -> bool:
        """배송 상태 업데이트"""
        try:
            return self.repository.update_delivery_status(delivery_id, new_status)
        except Exception as e:
            logger.error(f"배송 상태 업데이트 실패: {e}")
            return False

    def assign_driver(self, delivery_ids: List[str], driver_id: str) -> bool:
        """기사 할당"""
        try:
            return self.repository.assign_driver(delivery_ids, driver_id)
        except Exception as e:
            logger.error(f"기사 할당 실패: {e}")
            return False

    def get_drivers(self) -> List[Dict]:
        """기사 목록 조회"""
        try:
            return self.repository.get_drivers()
        except Exception as e:
            logger.error(f"기사 목록 조회 실패: {e}")
            return []
