import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from typing import Dict, Any
from src.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class WebCrawler:
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

    def wait_for_downloads(self):
        logger.info("다운로드가 완료될 때까지 대기합니다.")
        download_folder = self.config["DOWNLOAD_FOLDER"]
        end_time = time.time() + self.config["DOWNLOAD_WAIT_TIME"]

        while time.time() < end_time:
            downloaded_files = [
                filename for filename in os.listdir(download_folder)
                if not filename.endswith(".crdownload")
            ]

            if downloaded_files:
                logger.info(f"다운로드된 파일들: {downloaded_files}")
                logger.info("다운로드 완료.")
                return

            time.sleep(1)

        logger.error("다운로드가 시간 내에 완료되지 않았습니다.")
        raise TimeoutException("다운로드가 시간 내에 완료되지 않았습니다.")

    def login_and_process(self, username: str, password: str, start_date: str, end_date: str):
        try:
            logger.info("로그인 시도 중...")
            self.driver.get("https://cs.vinfiniti.biz:8227/")
            WebDriverWait(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.ID, "userName"))
            ).send_keys(username)
            WebDriverWait(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.NAME, "password"))
            ).send_keys(password)
            WebDriverWait(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.NAME, "project"))
            ).send_keys("cs")
            WebDriverWait(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
            ).click()
            logger.info("로그인 성공")

            logger.info("리포트 검색 중...")
            self.search_report()
            logger.info("리포트 검색 완료")

            logger.info(f"RMA 반환 처리 시작: {start_date}부터 {end_date}까지")
            self.process_rma_return(start_date, end_date)
            logger.info("RMA 반환 처리 완료")

        except Exception as e:
            logger.error(f"오류 발생: {str(e)}")
            raise
        finally:
            # 문제가 되는 close 호출 제거
            logger.info("프로세스가 완료되었습니다. 필요시 드라이버를 수동으로 종료하세요.")
            # self.driver.quit()  # 이 부분을 주석 처리하여 자동 종료를 방지

    def search_report(self):
        WebDriverWait(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
            EC.presence_of_element_located((By.ID, "ext-comp-1003"))
        )
        time.sleep(5)
        element = self.driver.find_element(By.ID, "ext-comp-1003")
        time.sleep(3)
        element.send_keys("repo")
        time.sleep(2)
        ActionChains(self.driver).send_keys("r").perform()
        element.send_keys(Keys.RETURN)

    def process_rma_return(self, start_date: str, end_date: str):
        try:
            WebDriverWait(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div:nth-child(28)"))
            )
            element = self.driver.find_element(By.CSS_SELECTOR, "div:nth-child(28)")
            element.click()
            action = ActionChains(self.driver)
            action.context_click(element).perform()
            time.sleep(1)
            action.send_keys(Keys.DOWN).send_keys(Keys.ENTER).perform()

            WebDriverWait(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.ID, "ext-comp-1045"))
            ).send_keys(start_date)

            WebDriverWait(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.ID, "ext-comp-1046"))
            ).send_keys(end_date)

            self.driver.find_element(By.ID, "ext-gen370").click()
            time.sleep(1)
            action.send_keys(Keys.ENTER).perform()

            WebDriverWait(self.driver, self.config["WEBDRIVER_TIMEOUT"]).until(
                EC.presence_of_element_located((By.ID, "ext-gen383"))
            ).click()
            action.send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.ENTER).perform()

            self.driver.find_element(By.ID, "ext-gen338").click()  # Confirm 클릭
            logger.info("Confirm 버튼 클릭 완료, 다운로드 대기 중...")

            # 다운로드가 완료될 때까지 대기
            self.wait_for_downloads()
            logger.info("다운로드가 완료되었습니다.")


        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logger.error(f"RMA 반환 처리 실패: {e.__class__.__name__} - {str(e)}")
            raise

