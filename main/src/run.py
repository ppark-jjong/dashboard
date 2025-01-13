from flask import Flask, jsonify
from src.repository.mysql_repository import MySQLRepository
from src.service.dashboard_service import DashboardService
from src.api.dash_routes import init_routes
from src.dash_view.index import init_dash
from src.model.main_model import Base  # SQLAlchemy Base 클래스
from sqlalchemy import MetaData, create_engine, text
import logging
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def initialize_database():
    """데이터베이스 초기화 및 메타데이터 반영"""
    try:
        logger.info("Initializing database metadata...")
        db_config = MySQLRepository().engine

        # 메타데이터 객체 생성 및 데이터베이스 상태 반영
        metadata = MetaData()
        metadata.reflect(bind=db_config)

        # 기존 테이블이 이미 있으면 생성하지 않음 (checkfirst=True)
        Base.metadata.create_all(bind=db_config, checkfirst=True)
        logger.info("Database metadata initialized successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database metadata: {e}")
        raise


def create_app():
    """Flask 애플리케이션 생성 및 설정"""
    try:
        server = Flask(__name__)
        server.config['DEBUG'] = True

        logger.info("Initializing MySQL repository...")
        mysql_repository = MySQLRepository()
        verify_mysql_connection(mysql_repository)

        # 데이터베이스 초기화
        initialize_database()

        logger.info("Initializing Dashboard service...")
        service = DashboardService(mysql_repo=mysql_repository)

        logger.info("Registering API routes...")
        api_routes = init_routes(service)
        server.register_blueprint(api_routes)

        logger.info("Initializing Dash app...")
        init_dash(server)

        # 디버그용: 등록된 라우트 확인
        for rule in server.url_map.iter_rules():
            logger.info(f"Registered route: {rule}")

        return server
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise


def verify_mysql_connection(repository):
    """데이터베이스 연결 테스트"""
    try:
        with repository.get_session() as session:
            session.execute(text("SELECT 1"))  # text로 쿼리 래핑
            logger.info("MySQL connection successful.")
    except Exception as e:
        logger.error(f"MySQL connection failed: {e}")
        raise


def main():
    """애플리케이션 실행"""
    try:
        app = create_app()
        logger.info("Starting the application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise


if __name__ == '__main__':
    main()
