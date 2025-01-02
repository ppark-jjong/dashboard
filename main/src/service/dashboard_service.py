from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from ..models.db_model import Delivery
from ..schemas.delivery_schema import DashboardDelivery, StatusUpdate, DriverAssignment
from src.config.cloud_sql import get_db
from src.config.redis_client import RedisClient


class DashboardService:
    def __init__(self):
        self.db: Session = next(get_db())
        self.redis_client = RedisClient()

    def get_dashboard_data(self) -> List[Dict[str, Any]]:
        """Redis에서 대시보드 데이터 조회"""
        try:
            return self.redis_client.get_dashboard_data()
        except Exception as e:
            print(f"Redis error: {e}")
            return self._get_and_cache_db_data()

    def refresh_dashboard_data(self) -> bool:
        """DB 데이터 조회 및 Redis 캐시 갱신"""
        try:
            return bool(self._get_and_cache_db_data())
        except Exception as e:
            print(f"Refresh error: {e}")
            return False

    def _get_and_cache_db_data(self) -> List[Dict[str, Any]]:
        """DB에서 데이터 조회 및 직렬화하여 Redis에 캐시"""
        deliveries = self.db.query(Delivery).all()

        # 직렬화는 한 번만 수행
        serialized_data = [
            DashboardDelivery.model_validate(delivery).model_dump()
            for delivery in deliveries
        ]

        # Redis에 직렬화된 데이터 저장
        self.redis_client.cache_dashboard_data(serialized_data)
        return serialized_data

    def update_delivery_status(self, status_update: StatusUpdate) -> bool:
        """배송 상태 업데이트"""
        try:
            delivery = self.db.query(Delivery).filter(
                Delivery.id == status_update.delivery_id
            ).first()

            if not delivery:
                return False

            delivery.status = status_update.new_status
            delivery.updated_at = datetime.utcnow()
            self.db.commit()

            # 변경된 데이터 직렬화하여 캐시 갱신
            self._get_and_cache_db_data()
            return True

        except Exception as e:
            self.db.rollback()
            print(f"Status update error: {e}")
            return False

    def assign_driver(self, assignment: DriverAssignment) -> bool:
        """기사 할당"""
        try:
            deliveries = self.db.query(Delivery).filter(
                Delivery.id.in_(assignment.delivery_ids)
            ).all()

            for delivery in deliveries:
                delivery.driver_id = assignment.driver_id
                if delivery.status == "WAITING":
                    delivery.status = "IN_PROGRESS"
                delivery.updated_at = datetime.utcnow()

            self.db.commit()

            # 변경된 데이터 직렬화하여 캐시 갱신
            self._get_and_cache_db_data()
            return True

        except Exception as e:
            self.db.rollback()
            print(f"Driver assignment error: {e}")
            return False