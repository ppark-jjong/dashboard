# src/models/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from main_project.config.base_config import DBConfig
import logging

logger = logging.getLogger(__name__)

# 데이터베이스 설정
config = DBConfig()
DATABASE_URL = f"mysql+pymysql://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}"

# 엔진 생성
engine = create_engine(
    DATABASE_URL,
    pool_size=5,  # 커넥션 풀 크기
    max_overflow=10,  # 최대 초과 커넥션
    pool_timeout=30,  # 커넥션 타임아웃 (초)
    pool_recycle=1800,  # 커넥션 재사용 시간 (초)
    echo=False  # SQL 로깅 여부
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# 모델 기본 클래스
Base = declarative_base()

# 세션 관리를 위한 컨텍스트 매니저
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# 데이터베이스 초기화 함수
def init_db():
    try:
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise