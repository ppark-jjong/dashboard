from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from service.auth_service import (
    create_session,
    verify_session,
    increment_login_attempts,
    reset_login_attempts,
)
import logging
from fastapi import APIRouter, Depends
from token_routes import require_token

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    user_id: str
    password: str


@router.post("/login")
async def login(request: LoginRequest):
    try:
        logger.info(f"로그인 시도: 사용자 ID={request.user_id}")
        if request.user_id != "testuser" or request.password != "password123":
            await increment_login_attempts(request.user_id)
            logger.warning(f"로그인 실패: 사용자 ID={request.user_id}")
            raise HTTPException(
                status_code=401, detail="잘못된 사용자 ID 또는 비밀번호"
            )

        await reset_login_attempts(request.user_id)
        session_token = await create_session(request.user_id)
        logger.info(f"로그인 성공: 사용자 ID={request.user_id}, 세션 생성 완료")
        return {
            "success": True,
            "message": "로그인 성공",
            "session_token": session_token,
        }
    except Exception as e:
        logger.error(f"로그인 처리 중 오류: {e}")
        raise HTTPException(
            status_code=500, detail="로그인 처리 중 오류가 발생했습니다."
        )


@router.get("/protected", dependencies=[Depends(require_token)])
async def protected_route(request: Request):
    try:
        session_token = request.headers.get("Authorization")
        if not session_token:
            logger.warning("세션 토큰이 제공되지 않았습니다.")
            raise HTTPException(status_code=401, detail="세션 토큰이 필요합니다.")

        session_data = await verify_session(session_token)
        logger.info(f"보호된 경로 접근: 사용자 ID={session_data['user_id']}")
        return {"success": True, "message": f"안녕하세요, {session_data['user_id']}님!"}
    except Exception as e:
        logger.error(f"보호된 경로 처리 중 오류: {e}")
        raise HTTPException(
            status_code=500, detail="보호된 경로 처리 중 오류가 발생했습니다."
        )


@router.post("/logout")
async def logout(request: Request):
    try:
        session_token = request.headers.get("Authorization")
        if not session_token:
            logger.warning("로그아웃 요청 시 세션 토큰이 제공되지 않았습니다.")
            raise HTTPException(status_code=401, detail="세션 토큰이 필요합니다.")

        await delete_session(session_token)
        logger.info(f"로그아웃 성공: 세션 토큰={session_token}")
        return {"success": True, "message": "로그아웃 성공"}
    except Exception as e:
        logger.error(f"로그아웃 처리 중 오류: {e}")
        raise HTTPException(
            status_code=500, detail="로그아웃 처리 중 오류가 발생했습니다."
        )
