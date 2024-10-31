from src.config.config_data import KafkaConfig
from src.config.config_google import GCSConfig, SheetsConfig
# from src.config.config_web_crawler import WebCrawlerConfig

class ConfigManager:
    kafka = KafkaConfig
    # spark = SparkConfig
    gcs = GCSConfig
    sheets = SheetsConfig
    # web_crawler = WebCrawlerConfig
