# src/model/mysql_repository.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging
from datetime import datetime, timedelta

from src.model.main_model import Driver, Dashboard, Delivery, Return
from src.config.base_config import DBConfig

logger = logging.getLogger(__name__)


class MySQLRepository:
    def __init__(self):
        """MySQL 데이터베이스 연결 초기화"""
        db_config = DBConfig()
        self.engine = create_engine(
            f"mysql+pymysql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=True
        )
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self):
        """동기 세션 컨텍스트 관리자"""
        session = self.Session()
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    def update_dashboard_data(self):
        """대시보드 데이터 동기화"""
        with self.get_session() as session:
            try:
                today = datetime.now()
                seven_days_later = today + timedelta(days=7)

                # 배송 데이터 조회
                logger.info("Querying delivery data...")
                deliveries = session.query(Delivery).filter(
                    Delivery.eta >= today,
                    Delivery.eta <= seven_days_later
                ).all()
                logger.info(f"Found {len(deliveries)} deliveries to process")

                for delivery in deliveries:
                    try:
                        logger.debug(f"Processing delivery {delivery.dps}")

                        # dps로 기존 데이터 조회
                        existing_dashboard = session.query(Dashboard).filter(
                            Dashboard.dps == delivery.dps
                        ).first()

                        if existing_dashboard:
                            # 기존 데이터 업데이트
                            logger.debug(f"Updating existing dashboard for delivery {delivery.dps}")
                            existing_dashboard.type = 'delivery'
                            existing_dashboard.dps = delivery.dps
                            existing_dashboard.status = delivery.status or '대기'
                            existing_dashboard.driver = delivery.driver
                            existing_dashboard.postal_code = delivery.postal_code
                            existing_dashboard.address = delivery.address
                            existing_dashboard.customer = delivery.customer
                            existing_dashboard.contact = delivery.contact
                            existing_dashboard.remark = delivery.remark
                            existing_dashboard.eta = delivery.eta
                            existing_dashboard.depart_time = delivery.depart_time
                            existing_dashboard.completed_time = delivery.completed_time
                            existing_dashboard.department = delivery.department
                            existing_dashboard.warehouse = delivery.warehouse
                            existing_dashboard.sla = delivery.sla

                            # delivery의 dashboard_id 업데이트
                            delivery.dashboard_id = existing_dashboard.id
                        else:
                            # 새로운 데이터 생성
                            logger.debug(f"Creating new dashboard for delivery {delivery.dps}")
                            dashboard = Dashboard(
                                type='delivery',
                                dps=delivery.dps,
                                status=delivery.status or '대기',
                                driver=delivery.driver,
                                postal_code=delivery.postal_code,
                                address=delivery.address,
                                customer=delivery.customer,
                                contact=delivery.contact,
                                remark=delivery.remark,
                                eta=delivery.eta,
                                depart_time=delivery.depart_time,
                                completed_time=delivery.completed_time,
                                department=delivery.department,
                                warehouse=delivery.warehouse,
                                sla=delivery.sla
                            )
                            session.add(dashboard)
                            session.flush()  # id 생성을 위한 flush

                            # delivery의 dashboard_id 업데이트
                            delivery.dashboard_id = dashboard.id

                    except Exception as item_error:
                        logger.error(f"Error processing delivery {delivery.dps}: {str(item_error)}")
                        continue

                # Return 데이터도 동일한 방식으로 처리
                returns = session.query(Return).filter(
                    Return.eta >= today,
                    Return.eta <= seven_days_later
                ).all()
                logger.info(f"Found {len(returns)} returns to process")

                for return_item in returns:
                    try:
                        logger.debug(f"Processing return {return_item.dps}")

                        # dps로 기존 데이터 조회
                        existing_dashboard = session.query(Dashboard).filter(
                            Dashboard.dps == return_item.dps
                        ).first()

                        if existing_dashboard:
                            # 기존 데이터 업데이트
                            logger.debug(f"Updating existing dashboard for return {return_item.dps}")
                            existing_dashboard.type = 'return'
                            existing_dashboard.dps = return_item.dps
                            existing_dashboard.status = return_item.status or '대기'
                            existing_dashboard.driver = return_item.driver
                            existing_dashboard.postal_code = return_item.postal_code
                            existing_dashboard.address = return_item.address
                            existing_dashboard.customer = return_item.customer
                            existing_dashboard.contact = return_item.contact
                            existing_dashboard.remark = return_item.remark
                            existing_dashboard.eta = return_item.eta
                            existing_dashboard.depart_time = None
                            existing_dashboard.completed_time = None
                            existing_dashboard.department = return_item.department
                            existing_dashboard.package_type = return_item.package_type
                            existing_dashboard.qty = return_item.qty

                            # return의 dashboard_id 업데이트
                            return_item.dashboard_id = existing_dashboard.id
                        else:
                            # 새로운 데이터 생성
                            logger.debug(f"Creating new dashboard for return {return_item.dps}")
                            dashboard = Dashboard(
                                type='return',
                                dps=return_item.dps,
                                status=return_item.status or '대기',
                                driver=return_item.driver,
                                postal_code=return_item.postal_code,
                                address=return_item.address,
                                customer=return_item.customer,
                                contact=return_item.contact,
                                remark=return_item.remark,
                                eta=return_item.eta,
                                depart_time=None,
                                completed_time=None,
                                department=return_item.department,
                                package_type=return_item.package_type,
                                qty=return_item.qty
                            )
                            session.add(dashboard)
                            session.flush()  # id 생성을 위한 flush

                            # return의 dashboard_id 업데이트
                            return_item.dashboard_id = dashboard.id

                    except Exception as item_error:
                        logger.error(f"Error processing return {return_item.dps}: {str(item_error)}")
                        continue

                logger.info("Committing transaction...")
                session.commit()
                logger.info("Dashboard data update completed successfully")
                return True

            except Exception as e:
                logger.error(f"Error syncing dashboard data: {str(e)}")
                if session.is_active:
                    session.rollback()
                raise
    def get_dashboard_items(self, skip: int, limit: int, filters: dict = None):
        """Dashboard 데이터 조회"""
        with self.get_session() as session:
            try:
                query = session.query(Dashboard)

                if filters:
                    if department := filters.get('department'):
                        query = query.filter(Dashboard.department == department)
                    if status := filters.get('status'):
                        query = query.filter(Dashboard.status == status)
                    if driver := filters.get('driver'):
                        query = query.filter(Dashboard.driver == driver)
                    if search := filters.get('search'):
                        search_pattern = f"%{search}%"
                        query = query.filter(
                            Dashboard.dps.like(search_pattern) |
                            Dashboard.customer.like(search_pattern)
                        )

                total = query.count()
                items = query.offset(skip).limit(limit).all()

                return items, total

            except Exception as e:
                logger.error(f"Error fetching dashboard items: {e}")
                raise

    def update_status(self, delivery_id: str, new_status: str, current_status: str):
        """상태 업데이트 및 시간 기록"""
        with self.get_session() as session:
            try:
                now = datetime.now()
                update_values = {'status': new_status}

                # 대기 -> 진행: 출발 시간 기록
                if current_status == '대기' and new_status == '진행':
                    update_values['depart_time'] = now

                # 진행 -> 완료/이슈: 완료 시간 기록
                elif current_status == '진행' and new_status in ['완료', '이슈']:
                    update_values['completed_time'] = now

                # Dashboard, Delivery, Return 테이블 상태 업데이트
                session.query(Dashboard).filter(Dashboard.dps == delivery_id).update(update_values)
                session.query(Delivery).filter(Delivery.dps == delivery_id).update(update_values)
                session.query(Return).filter(Return.dps == delivery_id).update({'status': new_status})

                session.commit()
                return True

            except Exception as e:
                logger.error(f"Error updating status: {e}")
                session.rollback()
                return False

    def assign_driver(self, delivery_ids: list, driver_id: str):
        """기사 할당"""
        with self.get_session() as session:
            try:
                session.query(Dashboard).filter(Dashboard.dps.in_(delivery_ids)).update({'driver': driver_id})
                session.query(Delivery).filter(Delivery.dps.in_(delivery_ids)).update({'driver': driver_id})
                session.query(Return).filter(Return.dps.in_(delivery_ids)).update({'driver': driver_id})

                session.commit()
                return True

            except Exception as e:
                logger.error(f"Error assigning driver: {e}")
                return False

    def get_drivers(self):
        """기사 목록 조회"""
        with self.get_session() as session:
            try:
                return session.query(Driver).all()
            except Exception as e:
                logger.error(f"Error fetching drivers: {e}")
                raise
