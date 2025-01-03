from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RedisConfig:
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', 6379))
    db: int = int(os.getenv('REDIS_DB', 0))
    password: Optional[str] = os.getenv('REDIS_PASSWORD')
    ssl: bool = os.getenv('REDIS_SSL', 'False').lower() == 'true'

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'password': self.password,
            'ssl': self.ssl,
            'decode_responses': True  # Redis 클라이언트 설정
        }


@dataclass
class MySQLConfig:
    host: str = os.getenv('MYSQL_HOST', 'localhost')
    port: int = int(os.getenv('MYSQL_PORT', 3306))
    user: str = os.getenv('MYSQL_USER', 'root')
    password: str = os.getenv('MYSQL_PASSWORD', '')
    database: str = os.getenv('MYSQL_DATABASE', 'delivery_system')
    charset: str = os.getenv('MYSQL_CHARSET', 'utf8mb4')

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'db': self.database,
            'charset': self.charset
        }