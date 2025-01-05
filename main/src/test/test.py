import asyncio

import pytest

from src.repository.redis_repository import RedisClient
from src.repository.mysql_repository import MySQLClient

@pytest.mark.asyncio
async def test_connections():
    redis_client = RedisClient()
    mysql_client = MySQLClient()

    # Redis 연결 확인
    if await redis_client.is_connected():
        print("Redis 연결 성공")
    else:
        print("Redis 연결 실패")

    # MySQL 연결 확인
    try:
        async with mysql_client.get_async_connection():
            print("MySQL 연결 성공")
    except Exception as e:
        print(f"MySQL 연결 실패: {e}")

asyncio.run(test_connections())

