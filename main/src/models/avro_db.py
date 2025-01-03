# src/models/avro_db.py
from datetime import datetime, date
from typing import Dict, Optional, Union
from .avro_base import AvroProcessor
import logging

logger = logging.getLogger(__name__)


class DBProcessor(AvroProcessor):
    """DB 데이터 처리를 위한 클래스"""

    def to_db_format(self, data: Dict, model_type: str = 'delivery') -> Dict:
        """Avro 데이터를 DB 포맷으로 변환"""
        try:
            logger.debug(f"Converting data to DB format. Type: {model_type}, DPS: {data.get('dps')}")
            result = {}

            # 모델 타입에 따른 스키마 선택
            schema = self._get_schema(model_type)

            for field in schema.fields:
                value = data.get(field.name)

                # timestamp-millis를 datetime으로 변환
                if (field.type.type == "long" and
                        field.type.get_prop("logicalType") == "timestamp-millis" and
                        value is not None):
                    try:
                        result[field.name] = datetime.fromtimestamp(value / 1000)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid timestamp value for {field.name}: {value}")
                        result[field.name] = None

                # date 타입 처리
                elif (field.type.type == "int" and
                      field.type.get_prop("logicalType") == "date" and
                      value is not None):
                    try:
                        result[field.name] = date.fromordinal(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid date value for {field.name}: {value}")
                        result[field.name] = None

                else:
                    result[field.name] = value

            logger.debug(f"Successfully converted data to DB format for DPS: {data.get('dps')}")
            return result

        except Exception as e:
            logger.error(f"Error converting data to DB format: {str(e)}")
            raise

    def from_db_format(self, data: Dict, model_type: str = 'delivery') -> Dict:
        """DB 데이터를 Avro 포맷으로 변환"""
        try:
            logger.debug(f"Converting DB data to Avro format. Type: {model_type}")
            result = {}

            # 모델 타입에 따른 스키마 선택
            schema = self._get_schema(model_type)

            for field in schema.fields:
                value = data.get(field.name)

                # datetime을 timestamp-millis로 변환
                if isinstance(value, datetime):
                    result[field.name] = int(value.timestamp() * 1000)

                # date를 ordinal로 변환
                elif isinstance(value, date):
                    result[field.name] = value.toordinal()

                else:
                    result[field.name] = value

            logger.debug("Successfully converted DB data to Avro format")
            return result

        except Exception as e:
            logger.error(f"Error converting DB data to Avro format: {str(e)}")
            raise

    def _get_schema(self, model_type: str):
        """모델 타입에 따른 스키마 반환"""
        schema_paths = {
            'delivery': 'schemas/delivery_model.avsc',
            'return': 'schemas/return_model.avsc',
            'driver': 'schemas/driver_model.avsc',
            'postal_code': 'schemas/postal_code_model.avsc'
        }

        if model_type not in schema_paths:
            raise ValueError(f"Unknown model type: {model_type}")

        return self.load_schema(schema_paths[model_type])

    def validate_db_data(self, data: Dict, model_type: str) -> bool:
        """DB 데이터 유효성 검증"""
        try:
            logger.debug(f"Validating DB data for type: {model_type}")

            schema = self._get_schema(model_type)

            # required 필드 검증
            for field in schema.fields:
                if not field.has_default and field.name not in data:
                    logger.warning(f"Required field missing: {field.name}")
                    return False

            # 타입 검증
            for field in schema.fields:
                value = data.get(field.name)
                if value is not None:
                    # timestamp 검증
                    if (field.type.type == "long" and
                            field.type.get_prop("logicalType") == "timestamp-millis"):
                        if not isinstance(value, (datetime, int, float)):
                            logger.warning(f"Invalid timestamp format for {field.name}: {value}")
                            return False

                    # date 검증
                    elif (field.type.type == "int" and
                          field.type.get_prop("logicalType") == "date"):
                        if not isinstance(value, (date, int)):
                            logger.warning(f"Invalid date format for {field.name}: {value}")
                            return False

            logger.debug("DB data validation successful")
            return True

        except Exception as e:
            logger.error(f"Error validating DB data: {str(e)}")
            return False