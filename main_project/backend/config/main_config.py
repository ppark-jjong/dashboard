from dataclasses import dataclass
import os
from typing import Any, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import aioredis
import logging

# 로깅 설정 개선
logging.basicConfig(
    level=logging.INFO,  # 프로덕션 환경에 더 적합한 로깅 레벨
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()
redis_pool: Optional[aioredis.Redis] = None


@dataclass
class BaseConfig:
    """설정 기본 클래스"""

    @staticmethod
    def get_env(key: str, default: Any = None) -> Any:
        value = os.getenv(key, default)
        logger.debug(
            f"환경변수 로딩: {key}=***"
            if "PASSWORD" in key
            else f"환경변수 로딩: {key}={value}"
        )
        return value

    @staticmethod
    def get_int_env(key: str, default: int = 0) -> int:
        try:
            return int(os.getenv(key, default))
        except (TypeError, ValueError):
            logger.warning(f"환경변수 {key} 변환 실패. 기본값 {default} 사용")
            return default


@dataclass
class RedisConfig(BaseConfig):
    """Redis 설정"""

    host: str = BaseConfig.get_env("REDIS_HOST", "redis")
    port: int = BaseConfig.get_int_env("REDIS_PORT", 6379)
    db: int = BaseConfig.get_int_env("REDIS_DB", 0)
    password: Optional[str] = BaseConfig.get_env("REDIS_PASSWORD")
    default_timeout: int = BaseConfig.get_int_env("REDIS_TIMEOUT", 300)
    pool_size: int = BaseConfig.get_int_env("REDIS_POOL_SIZE", 10)

    @property
    def url(self) -> str:
        """Redis URL 생성"""
        # 비밀번호 있는 경우와 없는 경우 처리
        if self.password:
            url = f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        else:
            url = f"redis://{self.host}:{self.port}/{self.db}"

        logger.debug(
            f"생성된 Redis URL: {url.replace(self.password, '***') if self.password else url}"
        )
        return url

    async def create_pool(self):
        """Redis 연결 풀 생성"""
        logger.info(f"Redis 연결 시도 - Host: {self.host}, Port: {self.port}")
        try:
            pool = await aioredis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                encoding="utf-8",
                decode_responses=True,
                max_connections=self.pool_size,
                socket_timeout=self.default_timeout,  # 타임아웃 추가
                socket_connect_timeout=self.default_timeout,  # 연결 타임아웃 추가
            )
            logger.info("Redis 연결 성공")
            return pool
        except Exception as e:
            logger.error(f"Redis 연결 실패: {e}")
            raise RuntimeError(f"Redis 연결 실패: {e}")


@dataclass
class DBConfig(BaseConfig):
    """데이터베이스 설정"""

    host: str = BaseConfig.get_env("MYSQL_HOST", "localhost")
    port: int = BaseConfig.get_int_env("MYSQL_PORT", 3306)
    user: str = BaseConfig.get_env("MYSQL_USER", "root")
    password: str = BaseConfig.get_env("MYSQL_PASSWORD", "1234")
    database: str = BaseConfig.get_env("MYSQL_DATABASE", "delivery_system")
    pool_size: int = BaseConfig.get_int_env("MYSQL_POOL_SIZE", 5)
    max_overflow: int = BaseConfig.get_int_env("MYSQL_MAX_OVERFLOW", 10)

    @property
    def url(self) -> str:
        """SQLAlchemy URL 생성"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def create_engine(self):
        """SQLAlchemy 엔진 생성"""
        return create_engine(
            self.url,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_pre_ping=True,
        )

    def create_session(self):
        """세션 팩토리 생성"""
        engine = self.create_engine()
        return sessionmaker(bind=engine)


@dataclass
class MainConfig:
    """메인 설정 클래스"""

    db: DBConfig = DBConfig()
    redis: RedisConfig = RedisConfig()


# 설정 인스턴스 생성
main_config = MainConfig()

# 데이터베이스 세션 팩토리 생성
SessionLocal = main_config.db.create_session()


async def init_redis():
    global redis_pool
    logger.info("Redis 풀 초기화 시도")
    try:
        redis_pool = await main_config.redis.create_pool()

        # 추가 로깅
        logger.info(f"Redis 풀 초기화 완료. 풀 객체: {redis_pool}")
        logger.info(f"Redis 풀 ID: {id(redis_pool)}")

        return redis_pool
    except Exception as e:
        logger.error(f"Redis 풀 초기화 실패: {e}")
        import traceback

        traceback.print_exc()
        raise


async def close_redis():
    """Redis 연결 풀 정리"""
    global redis_pool
    if redis_pool:
        logger.info("Closing Redis pool...")  # 종료 시작 로그
        try:
            await redis_pool.close()
            redis_pool = None
            logger.info("Redis pool closed successfully")  # 종료 성공 로그
        except Exception as e:
            logger.error(f"Error closing Redis pool: {e}")  # 종료 실패 로그
            raise
