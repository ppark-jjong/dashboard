# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from config.main_config import init_redis, redis_pool, SessionLocal
from service.dashboard_service import DashboardService
from api.main_routes import router as dashboard_router

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 추가
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])


@app.on_event("startup")
async def startup_event():
    try:
        logger.info("애플리케이션 시작 중...")

        # Redis 강제 초기화
        global redis_pool
        redis_pool = await init_redis()

        # DB 세션 생성
        db = SessionLocal()

        # Redis 동기화 서비스 초기화
        dashboard_service = DashboardService(db, redis_pool)

        # 대기 상태 작업 동기화
        await dashboard_service.sync_waiting_tasks()

        # 세션 닫기
        db.close()

        logger.info("Redis 풀 초기화 완료")
    except Exception as e:
        logger.error(f"애플리케이션 시작 실패: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    from config.main_config import close_redis

    await close_redis()
