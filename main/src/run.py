# src/run.py
from flask import Flask
from src.config.main_config import RedisConfig, MySQLConfig
from src.repository.redis_repository import RedisClient
from src.repository.mysql_repository import MySQLClient
from src.service.dashboard_service import DashboardService
from src.api.dash_routes import init_routes
from src.dash_view.index import init_dash
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    # Flask 서버 초기화
    server = Flask(__name__)

    try:
        # 데이터베이스 클라이언트 초기화
        redis_client = RedisClient()
        mysql_client = MySQLClient()

        # 서비스 초기화
        service = DashboardService(redis_client, mysql_client)

        # API 라우트 등록
        api_routes = init_routes(service)
        server.register_blueprint(api_routes, url_prefix='/')

        # Dash 앱 초기화
        app = init_dash(server)

        @server.route('/health')
        def health():
            try:
                redis_status = redis_client.ping()
                mysql_status = mysql_client.ping()
                return {
                    'status': 'healthy',
                    'redis': redis_status,
                    'mysql': mysql_status
                }
            except Exception as e:
                return {'status': 'unhealthy', 'error': str(e)}, 500

        return server

    except Exception as e:
        logger.error(f"Application initialization failed: {str(e)}")
        raise


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
