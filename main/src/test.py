from src.collectors.google_sheets import get_today_data, get_all_data
from kafka.producer import create_kafka_producer, send_to_kafka

# def main():
#     producer = create_kafka_producer()
#
#     # 오늘의 데이터 가져와 Kafka로 전송
#     today_data = get_today_data()
#     send_to_kafka(producer, 'today_delivery_data', today_data)
#
#     # 전체 데이터 가져와 Kafka로 전송
#     all_data = get_all_data()
#     send_to_kafka(producer, 'all_delivery_data', all_data)
#
# if __name__ == "__main__":
#     main()


import logging
from config.config_manager import ConfigManager
from collectors.web_crawler import WebCrawler, initialize_and_login

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # ConfigManager 초기화
    config_manager = ConfigManager()
    web_crawler_config = config_manager.get_web_crawler_config()

    # 테스트용 사용자 정보 설정
    username = "jhypark-dir"  # 실제 테스트 계정 사용자 이름으로 변경
    password = "Hyeok970209!@"  # 실제 테스트 계정 비밀번호로 변경

    # WebCrawler 초기화 및 로그인 테스트
    try:
        logger.info("WebCrawler를 초기화하고 로그인합니다.")
        crawler = initialize_and_login(web_crawler_config, username, password)
        logger.info("로그인 및 리포트 검색 완료")

        # 추가 테스트 작업 (예: 특정 기간의 RMA 반환 처리)
        start_date = "2024-10-01"
        end_date = "2024-10-07"
        logger.info(f"RMA 반환 프로세스를 시작합니다: {start_date}부터 {end_date}까지")
        crawler.process_rma_return(start_date, end_date)
        logger.info("RMA 반환 처리 완료")

    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {str(e)}")
    finally:
        # 작업 완료 후 드라이버 종료
        if 'crawler' in locals():
            crawler.close()
            logger.info("WebDriver를 종료했습니다.")

if __name__ == "__main__":
    main()
