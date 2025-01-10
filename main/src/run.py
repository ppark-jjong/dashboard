# src/run.py
from flask import Flask, jsonify
from src.repository.mysql_repository import MySQLRepository
from src.repository.redis_repository import RedisRepository
from src.service.dashboard_service import DashboardService
from src.api.dash_routes import init_routes
from src.dash_view.index import init_dash
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정 개선 - 콘솔 출력만 하도록 수정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 콘솔 출력용 핸들러만 사용
    ]
)
logger = logging.getLogger(__name__)


def create_app():
    """Flask 애플리케이션 생성 및 설정"""
    try:
        # Flask 서버 초기화
        server = Flask(__name__)

        # 디버그 모드 설정
        server.config['DEBUG'] = True

        # MySQL 리포지토리 초기화
        logger.info("Initializing MySQL repository...")
        mysql_repository = MySQLRepository()

        # Redis 리포지토리 초기화
        logger.info("Initializing Redis repository...")
        redis_repository = RedisRepository()

        # 서비스 계층 초기화
        logger.info("Initializing Dashboard service...")
        service = DashboardService(
            mysql_repo=mysql_repository,
            cache_repo=redis_repository
        )
        # API 라우트 등록
        logger.info("Registering API routes...")
        api_routes = init_routes(service)
        server.register_blueprint(api_routes)

        # 시스템 상태 확인용 엔드포인트
        @server.route('/health')
        def health():
            try:
                # MySQL 연결 테스트
                with mysql_repository.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        mysql_status = True
                        logger.info("Health check successful")
            except Exception as e:
                logger.error(f"MySQL health check failed: {e}")
                mysql_status = False

            return jsonify({
                'status': 'active',
                'mysql_connected': mysql_status
            }), 200 if mysql_status else 500

        # Dash 앱 초기화
        logger.info("Initializing Dash app...")
        dash_app = init_dash(server)
        logger.info("Dash app initialized successfully")

        return server

    except Exception as e:
        logger.error(f"Application initialization failed: {str(e)}")
        raise


def main():
    """애플리케이션 실행"""
    try:
        app = create_app()
        logger.info("Starting the application...")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()
