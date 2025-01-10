# src/config/base_config.py
from dataclasses import dataclass
import os
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BaseConfig:
    """설정 기본 클래스"""

    @staticmethod
    def get_env(key: str, default: Any = None) -> Any:
        return os.getenv(key, default)

    @staticmethod
    def get_int_env(key: str, default: int = 0) -> int:
        try:
            return int(os.getenv(key, default))
        except (TypeError, ValueError):
            return default


@dataclass
class DBConfig(BaseConfig):
    """데이터베이스 설정"""
    host: str = BaseConfig.get_env('DB_HOST', 'localhost')
    port: int = BaseConfig.get_int_env('DB_PORT', 3306)
    user: str = BaseConfig.get_env('DB_USER', 'root')
    password: str = BaseConfig.get_env('DB_PASSWORD', '')
    database: str = BaseConfig.get_env('DB_NAME', 'delivery_system')


@dataclass
class RedisConfig(BaseConfig):
    """Redis 설정"""
    host: str = BaseConfig.get_env('REDIS_HOST', 'localhost')
    port: int = BaseConfig.get_int_env('REDIS_PORT', 6379)
    db: int = BaseConfig.get_int_env('REDIS_DB', 0)
    password: str = BaseConfig.get_env('REDIS_PASSWORD', '')


@dataclass
class CacheConfig(BaseConfig):
    """캐시 설정"""
    driver_ttl: int = BaseConfig.get_int_env('CACHE_DRIVER_TTL', 3600)
    postal_code_ttl: int = BaseConfig.get_int_env('CACHE_POSTAL_TTL', 86400)
    dashboard_ttl: int = BaseConfig.get_int_env('CACHE_DASHBOARD_TTL', 300)