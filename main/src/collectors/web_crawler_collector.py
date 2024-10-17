import logging
import boto3
import time
import os
from typing import Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait as WB
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
logger = logging.getLogger(__name__)

class WebCrawlerCollector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.driver = self._initialize_driver()

    def _initialize_driver(self) -> webdriver.Chrome:
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.config["DOWNLOAD_FOLDER"],
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=chrome_options)

    def login(self) -> None:
        try:
            self.driver.get(self.config["LOGIN_URL"])
            WB(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.ID, "userName"))
            ).send_keys(self.config["USERNAME"])
            WB(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.NAME, "password"))
            ).send_keys(self.config["PASSWORD"])
            WB(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.NAME, "project"))
            ).send_keys("cs")
            WB(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
            ).click()
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logger.error(f"로그인 실패: {str(e)}")
            self.driver.quit()
            raise

    def download_report(self) -> str:
        try:
            WB(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.ID, "ext-comp-1003"))
            )
            time.sleep(5)
            element = self.driver.find_element(By.ID, "ext-comp-1003")
            time.sleep(3)
            element.send_keys("repo")
            time.sleep(2)
            element.send_keys(Keys.RETURN)
            time.sleep(5)  # 다운로드가 완료되기까지 잠시 대기
            download_path = os.path.join(self.config["DOWNLOAD_FOLDER"], "report.xlsx")
            if os.path.exists(download_path):
                return download_path
            else:
                raise FileNotFoundError("다운로드된 파일을 찾을 수 없습니다.")
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logger.error(f"보고서 다운로드 실패: {str(e)}")
            self.driver.quit()
            raise

    def upload_to_s3(self, file_path: str) -> None:
        try:
            s3 = boto3.client('s3')
            s3_key = os.path.basename(file_path)
            s3.upload_file(file_path, self.config["S3_BUCKET_NAME"], s3_key)
            logger.info(f"S3에 파일 업로드 완료: {s3_key}")
        except Exception as e:
            logger.error(f"S3 업로드 실패: {str(e)}")
            raise

    def close(self) -> None:
        self.driver.quit()


def run_crawler(config: Dict[str, Any]) -> None:
    crawler = WebCrawlerCollector(config)
    try:
        crawler.login()
        downloaded_file = crawler.download_report()
        # crawler.upload_to_s3(downloaded_file)
    except Exception as e:
        logger.error(f"크롤링 프로세스 중 오류 발생: {str(e)}")
    finally:
        crawler.close()

