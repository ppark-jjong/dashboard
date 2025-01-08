# src/repository/mysql_repository.py
import pymysql
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from contextlib import contextmanager
import logging

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()


class MySQLRepository:
    def __init__(self):
        self.config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', '1234'),
            'db': os.getenv('MYSQL_DATABASE', 'delivery_system'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

    @contextmanager
    def get_connection(self):
        """MySQL 연결 관리"""
        connection = pymysql.connect(**self.config)
        try:
            yield connection
        finally:
            connection.close()

    def get_dashboard_data(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # Delivery 데이터 조회
                delivery_query = """
                    SELECT 
                        d.department, 'delivery' as type, d.warehouse,
                        dr.driver_name, d.dps, d.sla, d.eta, d.status,
                        p.district, d.contact, d.address, d.customer,
                        d.remark, d.depart_time, p.duration_time
                    FROM delivery d
                    LEFT JOIN drivers dr ON d.driver_name = dr.driver_name
                    LEFT JOIN postal_code p ON d.postal_code = p.postal_code
                """

                # Return 데이터 조회
                return_query = """
                    SELECT 
                        r.department, 'return' as type, '' as warehouse,
                        dr.driver_name, r.dps, '' as sla, r.eta, r.status,
                        p.district, r.contact, r.address, r.customer,
                        r.remark, r.dispatch_date as depart_time, p.duration_time
                    FROM return r
                    LEFT JOIN drivers dr ON r.driver_name = dr.driver_name
                    LEFT JOIN postal_code p ON r.postal_code = p.postal_code
                """

                # UNION ALL로 두 쿼리 결합
                cursor.execute(f"{delivery_query} UNION ALL {return_query}")
                return cursor.fetchall()
