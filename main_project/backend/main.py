from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from config.main_config import init_redis, redis_pool, SessionLocal
from service.dashboard_service import DashboardService
from backend.api.dashboard_routes import router as dashboard_router
from api.auth_routes import router as auth_router

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])


# 글로벌 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"글로벌 예외 발생: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "서버에서 처리 중 오류가 발생했습니다."},
    )


@app.on_event("startup")
async def startup_event():
    try:
        logger.info("애플리케이션 시작 중...")
        global redis_pool
        redis_pool = await init_redis()
        logger.info("Redis 초기화 완료")
    except Exception as e:
        logger.error(f"애플리케이션 시작 실패: {e}")
        raise RuntimeError("애플리케이션 초기화 중 오류 발생")


@app.on_event("shutdown")
async def shutdown_event():
    from config.main_config import close_redis

    await close_redis()
    logger.info("애플리케이션 종료 완료")
