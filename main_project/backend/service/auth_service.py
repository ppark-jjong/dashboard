import uuid
import json
from fastapi import HTTPException
from config.main_config import redis_pool
import logging

logger = logging.getLogger(__name__)

SESSION_TTL = 3600
LOGIN_ATTEMPT_TTL = 300
MAX_LOGIN_ATTEMPTS = 5


async def create_session(user_id: str) -> str:
    try:
        session_token = str(uuid.uuid4())
        session_data = {"user_id": user_id}
        await redis_pool.set(
            f"session:{session_token}", json.dumps(session_data), ex=SESSION_TTL
        )
        logger.info(f"세션 생성: 사용자 ID={user_id}, 세션 토큰={session_token}")
        return session_token
    except Exception as e:
        logger.error(f"세션 생성 중 오류: {e}")
        raise HTTPException(status_code=500, detail="세션 생성 중 오류가 발생했습니다.")


async def verify_session(session_token: str):
    try:
        session_data = await redis_pool.get(f"session:{session_token}")
        if not session_data:
            logger.warning(f"유효하지 않은 세션: 토큰={session_token}")
            raise HTTPException(status_code=401, detail="세션이 유효하지 않습니다.")
        return json.loads(session_data)
    except Exception as e:
        logger.error(f"세션 검증 중 오류: {e}")
        raise HTTPException(status_code=500, detail="세션 검증 중 오류가 발생했습니다.")


async def increment_login_attempts(user_id: str):
    try:
        key = f"login_attempts:{user_id}"
        attempts = await redis_pool.incr(key)
        if attempts == 1:
            await redis_pool.expire(key, LOGIN_ATTEMPT_TTL)
        if attempts > MAX_LOGIN_ATTEMPTS:
            logger.warning(f"로그인 차단: 사용자 ID={user_id}")
            raise HTTPException(status_code=429, detail="로그인 시도가 너무 많습니다.")
        return attempts
    except Exception as e:
        logger.error(f"로그인 시도 제한 처리 중 오류: {e}")
        raise HTTPException(
            status_code=500, detail="로그인 시도 제한 처리 중 오류가 발생했습니다."
        )


async def reset_login_attempts(user_id: str):
    try:
        await redis_pool.delete(f"login_attempts:{user_id}")
        logger.info(f"로그인 시도 기록 초기화: 사용자 ID={user_id}")
    except Exception as e:
        logger.error(f"로그인 시도 초기화 중 오류: {e}")
        raise HTTPException(
            status_code=500, detail="로그인 시도 초기화 중 오류가 발생했습니다."
        )
