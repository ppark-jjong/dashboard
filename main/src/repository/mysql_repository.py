# src/repository/mysql_repository.py
import pymysql
from typing import Dict, List, Any, Optional
import logging
from contextlib import contextmanager
from src.config.base_config import DBConfig

logger = logging.getLogger(__name__)


class MySQLRepository:
    def __init__(self):
        logger.info("Initializing MySQLRepository")
        config = DBConfig()
        self.config = {
            'host': config.host,
            'port': config.port,
            'user': config.user,
            'password': config.password,
            'db': config.database,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        logger.info(f"MySQL Configuration loaded - Host: {self.config['host']}, Database: {self.config['db']}")

    @contextmanager
    def get_connection(self):
        """MySQL 연결 관리"""
        connection = None
        try:
            connection = pymysql.connect(**self.config)
            logger.debug("MySQL connection established")
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
                logger.debug("MySQL connection closed")

    def get_dashboard_data(self, page=1, page_size=15) -> Dict[str, Any]:
        """대시보드 데이터 조회"""
        logger.info("Fetching dashboard data")
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # 전체 레코드 수 조회
                    count_query = """
                        SELECT COUNT(*) as total FROM (
                            SELECT d.dps FROM delivery d
                            UNION ALL
                            SELECT r.dps FROM `return` r
                        ) as combined_data
                    """
                    cursor.execute(count_query)
                    total_records = cursor.fetchone()['total']

                    # 오프셋 계산
                    offset = (page - 1) * page_size

                    # Delivery 데이터 조회
                    delivery_query = f"""
                        SELECT 
                            d.department, 'delivery' as type, d.warehouse,
                            dr.driver_name, d.dps, d.sla, d.eta, d.status,
                            p.district as district, d.contact, d.address, d.customer,
                            d.remark, d.depart_time, p.duration_time
                        FROM delivery d
                        LEFT JOIN driver dr ON d.driver = dr.driver
                        LEFT JOIN postal_code p ON d.postal_code = p.postal_code
                    """

                    # Return 데이터 조회
                    return_query = f"""
                        SELECT 
                            r.department, 'return' as type, '' as warehouse,
                            dr.driver_name, r.dps, '' as sla, r.eta, r.status,
                            p.district as district, r.contact, r.address, r.customer,
                            r.remark, r.dispatch_date as depart_time, p.duration_time
                        FROM `return` r
                        LEFT JOIN driver dr ON r.driver = dr.driver
                        LEFT JOIN postal_code p ON r.postal_code = p.postal_code
                    """

                    full_query = f"""
                        {delivery_query}
                        UNION ALL
                        {return_query}
                        LIMIT {page_size} OFFSET {offset}
                    """

                    logger.debug(f"Executing query: {full_query}")
                    cursor.execute(full_query)
                    results = cursor.fetchall()
                    logger.info(f"Retrieved {len(results)} records")

                    return {
                        'data': results,
                        'total_records': total_records,
                        'page': page,
                        'page_size': page_size,
                        'total_pages': (total_records + page_size - 1) // page_size
                    }

                except Exception as e:
                    logger.error(f"Error fetching dashboard data: {str(e)}")
                    raise

    def update_delivery_status(self, delivery_id: str, new_status: str) -> bool:
        """배송 상태 업데이트"""
        logger.info(f"Updating status for delivery {delivery_id} to {new_status}")
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    query = """
                        UPDATE delivery 
                        SET status = %s,
                            completed_time = CASE 
                                WHEN %s = '완료' THEN NOW() 
                                ELSE NULL 
                            END
                        WHERE dps = %s
                    """
                    cursor.execute(query, (new_status, new_status, delivery_id))
                    conn.commit()
                    rows_affected = cursor.rowcount
                    logger.info(f"Status update affected {rows_affected} rows")
                    return rows_affected > 0
                except Exception as e:
                    logger.error(f"Error updating delivery status: {str(e)}")
                    conn.rollback()
                    return False

    def assign_driver(self, delivery_ids: List[str], driver_id: str) -> bool:
        """기사 할당"""
        logger.info(f"Assigning driver {driver_id} to deliveries: {delivery_ids}")
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    query = """
                        UPDATE delivery 
                        SET driver = %s,
                            dispatch_time = NOW()
                        WHERE dps IN %s
                    """
                    cursor.execute(query, (driver_id, tuple(delivery_ids)))
                    conn.commit()
                    rows_affected = cursor.rowcount
                    logger.info(f"Driver assignment affected {rows_affected} rows")
                    return rows_affected > 0
                except Exception as e:
                    logger.error(f"Error assigning driver: {str(e)}")
                    conn.rollback()
                    return False

    def get_drivers(self) -> List[Dict]:
        """기사 목록 조회"""
        logger.info("Fetching drivers list")
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    query = "SELECT driver, driver_name, driver_contact, driver_region FROM driver"
                    cursor.execute(query)
                    results = cursor.fetchall()
                    logger.info(f"Retrieved {len(results)} drivers")
                    return results
                except Exception as e:
                    logger.error(f"Error fetching drivers: {str(e)}")
                    raise
