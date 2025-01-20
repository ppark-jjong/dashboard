from typing import Generator, AsyncGenerator
from sqlalchemy.orm import Session
import aioredis
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from config.main_config import SessionLocal, redis_pool, init_redis
import logging

logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """Database 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """Redis 연결 의존성"""
    # Redis 풀이 없다면 초기화 시도
    if redis_pool is None:
        logger.warning("Redis 풀이 초기화되지 않았습니다. 동적 초기화 시도...")
        try:
            await init_redis()
        except Exception as e:
            logger.error(f"동적 Redis 초기화 실패: {e}")
            raise HTTPException(
                status_code=500, detail="Redis 연결을 초기화할 수 없습니다."
            )

    try:
        yield redis_pool
    except Exception as e:
        logger.error(f"Redis 연결 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="Redis 서버 연결 실패")
