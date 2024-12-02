from src.config.spark_config import SparkConfig
from src.config.gcp_config import GCPConfig

class ConfigManager:
    """
    설정 통합 관리 클래스
    """

    @staticmethod
    def get_spark_session():

        return SparkConfig.get_instance()

    @staticmethod
    def stop_spark_session():
        """
        SparkSession 종료
        """
        SparkConfig.stop_instance()

    @staticmethod
    def get_gcs_client():
        """
        GCS 클라이언트 반환
        """
        return GCPConfig.get_storage_client()
