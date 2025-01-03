# src/run.py
from flask import Flask, jsonify
from src.config.main_config import RedisConfig, MySQLConfig
from src.repository.redis_repository import RedisClient
from src.repository.mysql_repository import MySQLClient
from src.service.dashboard_service import DashboardService
from src.api.dash_routes import init_routes
from src.dash_view.index import init_dash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    server = Flask(__name__)

    # DB 클라이언트 초기화
    redis_client = None
    mysql_client = None

    try:
        redis_client = RedisClient()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}")

    try:
        mysql_client = MySQLClient()
        logger.info("MySQL connection successful")
    except Exception as e:
        logger.error(f"MySQL connection failed: {str(e)}")

    try:
        # DB 연결 여부와 관계없이 서비스 초기화
        service = DashboardService(redis_client, mysql_client)

        # REST API 엔드포인트 등록
        api_routes = init_routes(service)
        server.register_blueprint(api_routes, url_prefix='/api/dashboard')  # API 경로 변경

        # 시스템 상태 확인용 엔드포인트
        @server.route('/api/dashboard/health')
        def health():
            return jsonify({
                'status': 'active',
                'redis': redis_client is not None,
                'mysql': mysql_client is not None
            })

        # Dash 앱 초기화 (마지막에 실행)
        logger.info("Initializing Dash app...")
        app = init_dash(server)
        logger.info("Dash app initialized successfully")

    except Exception as e:
        logger.error(f"Service initialization warning: {str(e)}")

    return server


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )