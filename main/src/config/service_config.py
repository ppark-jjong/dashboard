import os
from dotenv import load_dotenv

# .env 파일 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

class GoogleSheetsConfig:
    API_KEY = os.getenv("GOOGLE_SHEETS_API_KEY_PATH")
    SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
    DATA_RANGE = os.getenv("GOOGLE_SHEETS_RANGE")

class RedisConfig:
    HOST = os.getenv("REDIS_HOST", "127.0.0.1")
    PORT = int(os.getenv("REDIS_PORT", 6379))
    PASSWORD = os.getenv("REDIS_PASSWORD")
    DB = int(os.getenv("REDIS_DB", 0))

class GCSConfig:
    BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    REGION = os.getenv("GCS_REGION", "asia-northeast3")
    FILE_PREFIX = os.getenv("GCS_FILE_PREFIX", "daily-data")

class PySparkConfig:
    MASTER = os.getenv("PYSPARK_MASTER", "local[*]")
    APP_NAME = os.getenv("PYSPARK_APP_NAME", "DefaultSparkApp")
    DRIVER_MEMORY = os.getenv("SPARK_DRIVER_MEMORY", "1g")
    EXECUTOR_MEMORY = os.getenv("SPARK_EXECUTOR_MEMORY", "2g")
