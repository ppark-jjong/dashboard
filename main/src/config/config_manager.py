from src.config.data_format import KafkaConfig
from src.config.google import GCSConfig, SheetsConfig, TimestampConfig
# from src.config.config_web_crawler import WebCrawlerConfig

class ConfigManager:
    kafka = KafkaConfig
    # spark = SparkConfig
    gcs = GCSConfig
    sheets = SheetsConfig
    # web_crawler = WebCrawlerConfig
    timestamp = TimestampConfig
    file_name = f"data_{timestamp.format_timestamp()}.csv"

