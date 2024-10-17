from config.config_manager import ConfigManager
from collectors.web_crawler_collector import run_crawler


def main():
    config_manager = ConfigManager()

    config = {
        "LOGIN_URL": "https://cs.vinfiniti.biz:8227/",
        "USERNAME": "jhypark-dir",  # 실제 사용자 이름
        "PASSWORD": "Hyeok970209!@",  # 실제 비밀번호
        "DOWNLOAD_FOLDER": config_manager.EXCEL_SAVE_PATH,
        "S3_BUCKET_NAME": config_manager.S3_BUCKET_NAME,
        "S3_REGION": config_manager.S3_REGION,
        "WEBDRIVER_TIMEOUT": 10,  # Selenium 타임아웃 설정
    }

    # 웹 크롤러 실행
    run_crawler(config)

if __name__ == "__main__":
    main()
