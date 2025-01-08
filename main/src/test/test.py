import asyncio
import logging
from src.repository.mysql_repository import MySQLRepository

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)


async def fetch_mysql_data(mysql_client):
    """MySQL에서 배송 데이터 가져오기"""
    try:
        deliveries = await mysql_client.get_deliveries()
        logger.info(f"MySQL에서 가져온 데이터 개수: {len(deliveries)}")
        return deliveries
    except Exception as e:
        logger.error(f"MySQL 데이터 가져오기 중 오류 발생: {e}")
        return []


async def store_data_to_redis(redis_client, data):
    """Redis에 데이터 저장 (Auto-Increment dashboard_id 사용)"""
    try:
        for item in data:
            # Redis에서 dashboard_id 생성
            dashboard_id = redis_client.redis.incr("dashboard:id")
            logger.info(f"생성된 dashboard_id: {dashboard_id}")

            # 데이터에 dashboard_id 추가
            item['dashboard_id'] = dashboard_id

            # Redis에 저장
            redis_key = f"dashboard:{dashboard_id}"
            logger.info(f"Redis에 데이터 저장: {redis_key}")
            await redis_client.set_dashboard_data(redis_key, item)
    except Exception as e:
        logger.error(f"Redis에 데이터 저장 중 오류 발생: {e}")


async def sync_mysql_to_redis():
    """MySQL 데이터를 Redis로 동기화"""
    logger.info("MySQL 데이터를 Redis로 동기화합니다.")

    mysql_client = MySQLClient()
    redis_client = RedisClient()

    # MySQL에서 데이터 가져오기
    mysql_data = await fetch_mysql_data(mysql_client)

    # Redis에 데이터 저장
    if mysql_data:
        await store_data_to_redis(redis_client, mysql_data)
        logger.info("MySQL 데이터를 Redis로 동기화 완료")
    else:
        logger.warning("MySQL에서 가져온 데이터가 없습니다.")


if __name__ == "__main__":
    asyncio.run(sync_mysql_to_redis())
