# src/run.py
from flask import Flask
from sqlalchemy import text, MetaData
from sqlalchemy.exc import SQLAlchemyError
from src.repository.mysql_repository import MySQLRepository
from src.repository.redis_repository import RedisRepository
from src.service.dashboard_service import DashboardService
from src.api.dash_routes import init_routes
from src.model.main_model import Base
from src.dash_view.index import init_dash  # Dash 앱 초기화 함수 임포트
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def create_app():
    try:
        server = Flask(__name__)
        server.config['SERVER_NAME'] = '127.0.0.1:5000'

        # MySQL 초기화
        mysql_repository = MySQLRepository()
        verify_mysql_connection(mysql_repository)

        # Redis 초기화
        redis_repository = RedisRepository()

        # 데이터베이스 초기화
        initialize_database(mysql_repository)

        # 서비스 초기화
        service = DashboardService(mysql_repository, redis_repository)

        # API 라우트 등록
        api_routes = init_routes(service)
        server.register_blueprint(api_routes)

        # Dash 앱 초기화
        dash_app = init_dash(server)

        return server

    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise

def initialize_database(repository):
    """데이터베이스 초기화"""
    try:
        logger.info("Initializing database metadata...")
        metadata = MetaData()
        metadata.reflect(bind=repository.engine)
        Base.metadata.create_all(bind=repository.engine, checkfirst=True)
        logger.info("Database initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {e}")
        raise


def verify_mysql_connection(repository):
    """MySQL 연결 확인"""
    try:
        with repository.get_session() as session:
            session.execute(text("SELECT 1"))
            logger.info("MySQL connection verified")
    except Exception as e:
        logger.error(f"MySQL connection failed: {e}")
        raise


def main():
    """애플리케이션 실행"""
    try:
        app = create_app()
        logger.info("Starting application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise


if __name__ == '__main__':
    main()
