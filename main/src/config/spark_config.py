from pyspark.sql import SparkSession
from src.config.logger import Logger

logger = Logger.get_logger(__name__)


class SparkConfig:
    # SparkSession 관리 클래스 (싱글톤 패턴)
    _spark_instance = None

    @staticmethod
    def get_instance(app_name="DataProcessing", master="local[*]", executor_memory="2g"):
        """
        SparkSession 인스턴스 반환. 없으면 새로 생성.
        :param app_name: 애플리케이션 이름
        :param master: Spark Master 설정
        :param executor_memory: 실행 메모리 크기
        """
        if SparkConfig._spark_instance is None:
            try:
                logger.info("SparkSession 초기화 중...")
                SparkConfig._spark_instance = SparkSession.builder \
                    .appName(app_name) \
                    .master(master) \
                    .config("spark.executor.memory", executor_memory) \
                    .getOrCreate()
                logger.info("SparkSession 초기화 완료.")
            except Exception as e:
                logger.error(f"SparkSession 초기화 실패: {e}")
                raise RuntimeError("SparkSession을 초기화할 수 없습니다.")
        return SparkConfig._spark_instance

    #   SparkSession 종료
    @staticmethod
    def stop_instance():
        if SparkConfig._spark_instance is not None:
            logger.info("SparkSession 종료 중...")
            SparkConfig._spark_instance.stop()
            SparkConfig._spark_instance = None
            logger.info("SparkSession 종료 완료.")
