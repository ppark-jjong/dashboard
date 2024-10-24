import logging
from config.config_manager import ConfigManager
from collectors.web_crawler import WebCrawler

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    config_manager = ConfigManager()
    web_crawler_config = config_manager.get_web_crawler_config()

    username = "jhypark-dir"
    password = "Hyeok970209!@"
    start_date = "2024-10-01"
    end_date = "2024-10-07"

    try:
        logger.info("WebCrawler를 초기화합니다.")
        crawler = WebCrawler(web_crawler_config)
        crawler.login_and_process(username, password, start_date, end_date)
        logger.info("WebCrawler 작업 완료")
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
