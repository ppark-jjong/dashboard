from sqlalchemy.orm import Session
import aioredis
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from backend.model.board_model import Driver, Delivery, Return, PostalCode
import logging

logger = logging.getLogger(__name__)


class MySQLRepository:
    def __init__(self, db: Session):
        self.db = db  # db 세션 초기화 추가

    def get_waiting_tasks(self):
        try:
            # Delivery와 PostalCode 조인 조회
            deliveries = (
                self.db.query(Delivery)
                .join(PostalCode, Delivery.postal_code == PostalCode.postal_code)
                .filter(Delivery.status == "대기")
                .all()
            )

            # Return과 PostalCode 조인 조회
            returns = (
                self.db.query(Return)
                .join(PostalCode, Return.postal_code == PostalCode.postal_code)
                .filter(Return.status == "대기")
                .all()
            )

            return {"deliveries": deliveries, "returns": returns}
        except Exception as e:
            print(f"Error getting waiting tasks: {e}")
            return {"deliveries": [], "returns": []}

    def sync_task_status(
        self, task_type: str, dps: str, status: str, driver_id: Optional[int] = None
    ) -> bool:
        try:
            if task_type == "delivery":
                task = self.db.query(Delivery).filter(Delivery.dps == dps).first()
            else:
                task = self.db.query(Return).filter(Return.dps == dps).first()

            if not task:
                return False

            task.status = status
            if driver_id is not None:
                task.driver = driver_id

            if status == "진행":
                if isinstance(task, Delivery):
                    task.depart_time = datetime.now()
                else:
                    task.dispatch_date = datetime.now()
            elif status in ["완료", "이슈"]:
                if isinstance(task, Delivery):
                    task.completed_time = datetime.now()

            self.db.commit()  # self.session → self.db
            return True
        except Exception as e:
            self.db.rollback()  # self.session → self.db
            raise e
