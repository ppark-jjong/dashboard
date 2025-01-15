# src/repository/mysql_repository.py
from contextlib import contextmanager

from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional
import logging

from main_project.config.base_config import DBConfig
from main_project.model.main_model import Driver, Dashboard, Delivery, Return, PostalCode

logger = logging.getLogger(__name__)


class MySQLRepository:
    def __init__(self):
        try:
            db_config = DBConfig()
            self.engine = create_engine(
                f"mysql+pymysql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}",
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )
            self.Session = sessionmaker(bind=self.engine)
            logger.info("MySQL repository initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MySQL repository: {e}")
            raise

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    def sync_dashboard_data(self) -> bool:
        """대시보드 데이터 동기화"""
        try:
            with self.get_session() as session:
                current_time = datetime.now()
                week_later = current_time + timedelta(days=7)

                delivery_data = (
                    session.query(
                        Delivery,
                        PostalCode.district,
                        PostalCode.duration_time,
                        Driver.driver_name,
                        Driver.driver_contact
                    )
                    .outerjoin(PostalCode, Delivery.postal_code == PostalCode.postal_code)
                    .outerjoin(Driver, Delivery.driver == Driver.driver)
                    .filter(Delivery.eta.between(current_time, week_later))
                    .all()
                )

                return_data = (
                    session.query(
                        Return,
                        PostalCode.district,
                        PostalCode.duration_time,
                        Driver.driver_name,
                        Driver.driver_contact
                    )
                    .outerjoin(PostalCode, Return.postal_code == PostalCode.postal_code)
                    .outerjoin(Driver, Return.driver == Driver.driver)
                    .filter(Return.eta.between(current_time, week_later))
                    .all()
                )

                dashboard_records = []

                for delivery, district, duration_time, driver_name, driver_contact in delivery_data:
                    dashboard_records.append({
                        'type': 'delivery',
                        'dps': delivery.dps,
                        'status': delivery.status,
                        'department': delivery.department,
                        'postal_code': delivery.postal_code,
                        'district': district,
                        'duration_time': duration_time,
                        'address': delivery.address,
                        'customer': delivery.customer,
                        'contact': delivery.contact,
                        'remark': delivery.remark,
                        'eta': delivery.eta,
                        'warehouse': delivery.warehouse,
                        'sla': delivery.sla,
                        'driver_id': delivery.driver,
                        'driver_name': driver_name,
                        'driver_contact': driver_contact
                    })

                for return_item, district, duration_time, driver_name, driver_contact in return_data:
                    dashboard_records.append({
                        'type': 'return',
                        'dps': return_item.dps,
                        'status': return_item.status,
                        'department': return_item.department,
                        'postal_code': return_item.postal_code,
                        'district': district,
                        'duration_time': duration_time,
                        'address': return_item.address,
                        'customer': return_item.customer,
                        'contact': return_item.contact,
                        'remark': return_item.remark,
                        'eta': return_item.eta,
                        'driver_id': return_item.driver,
                        'driver_name': driver_name,
                        'driver_contact': driver_contact
                    })

                if dashboard_records:
                    session.query(Dashboard).delete()
                    session.bulk_insert_mappings(Dashboard, dashboard_records)
                    session.commit()

                return True

        except SQLAlchemyError as e:
            logger.error(f"Database error during dashboard sync: {e}")
            raise
        except Exception as e:
            logger.error(f"Error syncing dashboard data: {e}")
            raise

    def get_dashboard_items(
            self,
            skip: int,
            limit: int,
            filters: Dict
    ) -> Tuple[List[Dashboard], int]:
        """대시보드 데이터 조회"""
        try:
            with self.get_session() as session:
                query = session.query(Dashboard)

                if filters:
                    if department := filters.get('department'):
                        query = query.filter(Dashboard.department == department)
                    if status := filters.get('status'):
                        query = query.filter(Dashboard.status == status)
                    if driver := filters.get('driver'):
                        query = query.filter(Dashboard.driver_id == driver)
                    if search := filters.get('search'):
                        search_pattern = f"%{search}%"
                        query = query.filter(or_(
                            Dashboard.dps.like(search_pattern),
                            Dashboard.customer.like(search_pattern),
                            Dashboard.address.like(search_pattern)
                        ))

                total = query.count()
                items = query.order_by(Dashboard.eta).offset(skip).limit(limit).all()

                return items, total

        except SQLAlchemyError as e:
            logger.error(f"Database error during dashboard items retrieval: {e}")
            raise

    def get_dashboard_item(self, dps: str) -> Optional[Dashboard]:
        """개별 대시보드 아이템 조회"""
        try:
            with self.get_session() as session:
                return session.query(Dashboard).filter(Dashboard.dps == dps).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error during dashboard item retrieval: {e}")
            raise

    def update_status(
            self,
            delivery_id: str,
            new_status: str,
            current_status: str
    ) -> bool:
        """상태 업데이트"""
        try:
            with self.get_session() as session:
                now = datetime.now()
                update_values = {'status': new_status}

                if current_status == '대기' and new_status == '진행':
                    update_values['depart_time'] = now
                elif current_status == '진행' and new_status in ['완료', '이슈']:
                    update_values['completed_time'] = now

                session.query(Dashboard).filter(
                    Dashboard.dps == delivery_id
                ).update(update_values)

                return True

        except SQLAlchemyError as e:
            logger.error(f"Database error during status update: {e}")
            raise

    def assign_driver(self, delivery_ids: List[str], driver_id: int) -> bool:
        """기사 할당"""
        try:
            with self.get_session() as session:
                # 1. 기사 정보 조회
                driver = session.query(Driver).filter(Driver.driver == driver_id).first()
                if not driver:
                    logger.error(f"No driver found with ID: {driver_id}")
                    return False

                # 2. 대시보드 업데이트
                affected = session.query(Dashboard).filter(
                    Dashboard.dps.in_(delivery_ids)
                ).update({
                    'driver_id': driver_id,
                    'driver_name': driver.driver_name,
                    'driver_contact': driver.driver_contact,
                    'status': '대기'  # 기사 할당 시 상태 초기화
                }, synchronize_session=False)

                if affected > 0:
                    logger.info(f"Assigned driver {driver_id} to {affected} dashboard items")
                    return True
                return False

        except SQLAlchemyError as e:
            logger.error(f"Database error during driver assignment: {e}")
            raise


    def get_drivers(self) -> List[Driver]:
        """기사 목록 조회"""
        try:
            with self.get_session() as session:
                return session.query(Driver).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error during drivers retrieval: {e}")
            raise

    def get_dashboard_detail(self, dps: str) -> Optional[Dict]:
        """상세 정보 조회"""
        try:
            with self.get_session() as session:
                item = session.query(Dashboard).filter(Dashboard.dps == dps).first()
                if not item:
                    return None

                return {
                    'department': item.department,
                    'type': item.type,
                    'warehouse': item.warehouse,
                    'driver_name': item.driver_name,
                    'dps': item.dps,
                    'sla': item.sla,
                    'status': item.status,
                    'eta': item.eta,
                    'address': item.address,
                    'customer': item.customer,
                    'contact': item.contact,
                    'remark': item.remark,
                    'district': item.district,
                    'duration_time': item.duration_time,
                    'depart_time': item.depart_time,
                    'completed_time': item.completed_time,
                    'driver_contact': item.driver_contact
                }

        except SQLAlchemyError as e:
            logger.error(f"Database error during detail retrieval: {e}")
            raise
