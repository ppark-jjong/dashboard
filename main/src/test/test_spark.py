from src.config.manager_config import ConfigManager
from src.processors.process_data import process_and_save_data
if __name__ == "__main__":
    try:
        # SparkSession 생성
        spark = ConfigManager.get_spark_session()

        # 데이터 로드, 처리 및 저장
        process_and_save_data(spark)
    except Exception as e:
        print(f"전체 프로세스 실패: {e}")
    finally:
        # SparkSession 종료
        ConfigManager.stop_spark_session()
