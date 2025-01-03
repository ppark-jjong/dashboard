import aiomysql
import pymysql
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from ..config.main_config import MySQLConfig

load_dotenv()


class MySQLClient:
    def __init__(self, config: Optional[MySQLConfig] = None):
        self.config = config or MySQLConfig()

    @asynccontextmanager
    async def get_async_connection(self):
        """비동기 DB 연결 관리"""
        pool = await aiomysql.create_pool(**self.config)
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                yield cursor
            await conn.commit()
        pool.close()
        await pool.wait_closed()

    async def get_deliveries(self) -> List[Dict[str, Any]]:
        """배송 데이터 조회"""
        async with self.get_async_connection() as cursor:
            await cursor.execute("""
                SELECT d.*, p.duration_time
                FROM delivery d
                LEFT JOIN postal_code p ON d.postal_code = p.postal_code
                ORDER BY d.eta ASC
            """)
            return await cursor.fetchall()

    async def get_returns(self) -> List[Dict[str, Any]]:
        """회수 데이터 조회"""
        async with self.get_async_connection() as cursor:
            await cursor.execute("""
                SELECT *
                FROM return
                ORDER BY eta ASC
            """)
            return await cursor.fetchall()

    async def update_delivery_status(self, dps: int, status: str) -> bool:
        """배송 상태 업데이트"""
        try:
            async with self.get_async_connection() as cursor:
                await cursor.execute("""
                    UPDATE delivery
                    SET status = %s,
                        last_updated = NOW()
                    WHERE dps = %s
                """, (status, dps))
                return True
        except Exception as e:
            print(f"MySQL update delivery status error: {e}")
            return False

    async def update_return_status(self, dps: int, status: str) -> bool:
        """회수 상태 업데이트"""
        try:
            async with self.get_async_connection() as cursor:
                await cursor.execute("""
                    UPDATE return
                    SET status = %s,
                        last_updated = NOW()
                    WHERE dps = %s
                """, (status, dps))
                return True
        except Exception as e:
            print(f"MySQL update return status error: {e}")
            return False

    async def update_delivery(self, dps: int, updates: Dict[str, Any]) -> bool:
        """배송 정보 업데이트"""
        try:
            set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
            values = list(updates.values()) + [dps]

            async with self.get_async_connection() as cursor:
                await cursor.execute(f"""
                    UPDATE delivery
                    SET {set_clause},
                        last_updated = NOW()
                    WHERE dps = %s
                """, values)
                return True
        except Exception as e:
            print(f"MySQL update delivery error: {e}")
            return False

    async def update_return(self, dps: int, updates: Dict[str, Any]) -> bool:
        """회수 정보 업데이트"""
        try:
            set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
            values = list(updates.values()) + [dps]

            async with self.get_async_connection() as cursor:
                await cursor.execute(f"""
                    UPDATE return
                    SET {set_clause},
                        last_updated = NOW()
                    WHERE dps = %s
                """, values)
                return True
        except Exception as e:
            print(f"MySQL update return error: {e}")
            return False
