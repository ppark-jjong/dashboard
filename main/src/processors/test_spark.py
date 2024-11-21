from pyspark.sql import SparkSession
from src.config.config_manager import ConfigManager
from src.processors import process_common
from src.config.logger import Logger

logger = Logger.get_logger(__name__)


def read_data(spark: SparkSession, file_path: str):
    logger.info(f"Reading data from {file_path}")
    return spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(file_path)


# def perform_analysis(df_clean):
#     # 예시: 지역별 배송량 집계
#     df_region = df_clean.groupBy("Region").count().withColumnRenamed("count", "DeliveryCount")
#     # BigQuery에 저장 (실제 테이블 이름과 데이터셋으로 변경하세요)
#     df_region.write.format('bigquery') \
#         .option('table', 'your_dataset.regional_trends') \
#         .save()


def main():
    try:
        # SparkSession 초기화
        spark = ConfigManager.spark.get_instance(master="local[*]")  # 필요 시 설정 변경
        logger.info("Spark session started.")

        # 데이터 로드
        df_raw = read_data(spark, "C:\MyMain\dashboard\etc\CS_Delivery Report.csv")
        logger.info("데이터 로드 성공.")

        # 결측값 조건 생성
        null_condition = process_common.create_null_condition(df_raw)
        logger.info("결측값 조건 파악")

        # 데이터 분리: 결측값이 있는 행과 없는 행
        df_missing, df_clean = process_common.split_data_by_nulls(df_raw, null_condition)
        logger.info("결측값 분리")

        # 결측값이 있는 데이터 저장
        process_common.save_missing_data(df_missing, "path_to_save_missing_data.csv")

        # 데이터 전처리 및 특징 추출
        df_clean = process_common.preprocess_data(df_clean)

        # 지역 매핑 데이터 조인 (필요한 경우)
        # df_clean = process_common.join_region_data(df_clean, spark, "path_zip_to_region.csv")

        # df_clean 캐시
        df_clean.cache()
        logger.info("결측값 처리된 df 캐시 저장")

        # 분석 수행
        # perform_analysis(df_clean)
        logger.info("분석 수행 완료.")

        # 캐시 해제
        df_clean.unpersist()
        logger.info("캐시 종료")

    except Exception as e:
        logger.error(f"에러 발생 : {e}")
    finally:
        # Spark 세션 종료
        spark.stop_session()
        logger.info("Spark session stopped.")


if __name__ == "__main__":
    main()
