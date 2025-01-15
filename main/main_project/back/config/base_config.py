# src/config/base_config.py
from dataclasses import dataclass
import os
from typing import Any
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
    host: str = BaseConfig.get_env('MYSQL_HOST', 'localhost')
    port: int = BaseConfig.get_int_env('MYSQL_PORT', 3306)
    user: str = BaseConfig.get_env('MYSQL_USER', 'root')
    password: str = BaseConfig.get_env('MYSQL_PASSWORD', '1234')
    database: str = BaseConfig.get_env('MYSQL_DATABASE', 'delivery_system')

@dataclass
class RedisConfig(BaseConfig):
    """Redis 설정"""
    host: str = BaseConfig.get_env('REDIS_HOST', 'localhost')
    port: int = BaseConfig.get_int_env('REDIS_PORT', 6379)
    db: int = BaseConfig.get_int_env('REDIS_DB', 0)
    password: str = BaseConfig.get_env('REDIS_PASSWORD', None)
    default_timeout: int = BaseConfig.get_int_env('REDIS_TIMEOUT', 300)  # 5분