from selenium import webdriver

class WebCrawlerConfig:
    DOWNLOAD_FOLDER = "/app/downloads"
    WEBDRIVER_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    DOWNLOAD_WAIT_TIME = 120

    @staticmethod
    def get_web_driver():
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": WebCrawlerConfig.DOWNLOAD_FOLDER,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=chrome_options)
