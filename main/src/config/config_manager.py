from src.config.config_format import KafkaConfig, SparkConfig, DashBoardConfig
from src.config.config_google import GCSConfig, SheetsConfig, TimestampConfig

class ConfigManager:
    kafka = KafkaConfig
    spark = SparkConfig
    dashboard = DashBoardConfig
    gcs = GCSConfig
    sheets = SheetsConfig
    # web_crawler = WebCrawlerConfig
    timestamp = TimestampConfig
    file_name = f"data_{timestamp.format_timestamp()}.csv"
