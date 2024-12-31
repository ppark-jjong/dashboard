from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import os

# Database configuration
DB_USER = os.getenv("DB_USER", "your-db-user")
DB_PASS = os.getenv("DB_PASS", "your-db-password")
DB_NAME = os.getenv("DB_NAME", "your-db-name")
DB_HOST = os.getenv("DB_HOST", "your-db-host")

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """데이터베이스 세션 생성 및 관리"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()