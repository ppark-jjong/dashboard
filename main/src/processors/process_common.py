from src.config.logger import Logger
from pyspark.sql.functions import (
    col, isnan, to_date, to_timestamp, hour, date_format
)
from functools import reduce


logger = Logger.get_logger(__name__)



def create_null_condition(df):
    """
    데이터프레임의 모든 컬럼에 대한 결측값 체크 조건을 생성합니다.
    """
    null_conditions = [col(c).isNull() | isnan(col(c)) for c in df.columns]
    return reduce(lambda x, y: x | y, null_conditions)


def split_data_by_nulls(df, null_condition):
    """
    결측값이 있는 행과 없는 행으로 데이터를 분리합니다.
    """
    df_missing = df.filter(null_condition)
    df_clean = df.filter(~null_condition)
    return df_missing, df_clean


def save_missing_data(df_missing, save_path: str):
    """
    결측값이 있는 데이터를 저장합니다.
    """
    df_missing.write.format("csv") \
        .option("header", "true") \
        .mode("overwrite") \
        .save(save_path)


def preprocess_data(df_clean):
    """
    데이터 전처리 및 특징 추출을 수행합니다.
    """
    df_clean = df_clean.withColumn("Date", to_date(col("Date"), "yyyy-MM-dd")) \
        .withColumn("ETA", to_timestamp(col("ETA"), "yyyy-MM-dd HH:mm")) \
        .withColumn("Hour", hour(col("ETA"))) \
        .withColumn("DayOfWeek", date_format(col("ETA"), 'E'))
    return df_clean

# def join_region_data(df_clean, spark, region_mapping_path: str):
#     """
#     지역 매핑 데이터를 조인합니다.
#     """
#     zip_region_mapping = spark.read.format("csv") \
#         .option("header", "true") \
#         .load(region_mapping_path)
#     df_clean = df_clean.join(zip_region_mapping, on="Zip Code", how="left")
#     return df_clean
