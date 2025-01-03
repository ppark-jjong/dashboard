# src/models/avro_redis.py
from datetime import datetime, date
from typing import Dict, Optional
from .avro_base import AvroProcessor
import logging

logger = logging.getLogger(__name__)


class RedisProcessor(AvroProcessor):
    """Redis 데이터 처리를 위한 클래스"""

    def to_redis_hash(self, data: Dict) -> Dict:
        """Avro 데이터를 Redis hash 형식으로 변환"""
        try:
            logger.debug(f"Converting data to Redis hash format for DPS: {data.get('dps')}")
            result = {}

            # delivery_type enum 처리
            if data.get('delivery_type'):
                if data['delivery_type'] not in ['delivery', 'return']:
                    logger.warning(f"Invalid delivery_type: {data['delivery_type']} for DPS: {data.get('dps')}")
                    data['delivery_type'] = 'delivery'  # 기본값 설정

            # 필드 변환
            for field in self.schema.fields:
                value = data.get(field.name)

                if value is None:
                    result[field.name] = ""
                    continue

                # timestamp-millis 처리
                if (field.type.type == "long" and
                        field.type.get_prop("logicalType") == "timestamp-millis"):
                    if isinstance(value, datetime):
                        result[field.name] = str(int(value.timestamp() * 1000))
                    elif isinstance(value, (int, float)):
                        result[field.name] = str(int(value))
                    else:
                        result[field.name] = ""

                # 정수형 처리
                elif field.type.type in ["int", "long"]:
                    result[field.name] = str(value)

                # enum 처리 (delivery_type)
                elif field.type.type == "enum":
                    if value in field.type.symbols:
                        result[field.name] = value
                    else:
                        result[field.name] = field.type.symbols[0]  # 기본값 사용

                # 나머지는 문자열로 변환
                else:
                    result[field.name] = str(value)

            logger.debug(f"Successfully converted data for DPS: {data.get('dps')}")
            return result

        except Exception as e:
            logger.error(f"Error converting data to Redis hash: {str(e)}")
            raise

    def from_redis_hash(self, hash_data: Dict) -> Dict:
        """Redis hash 데이터를 Avro 형식으로 변환"""
        try:
            logger.debug("Converting Redis hash data to Avro format")
            result = {}

            for field in self.schema.fields:
                value = hash_data.get(field.name, "")

                if value == "":
                    result[field.name] = None
                    continue

                # timestamp-millis 처리
                if (field.type.type == "long" and
                        field.type.get_prop("logicalType") == "timestamp-millis"):
                    try:
                        result[field.name] = int(value)
                    except ValueError:
                        result[field.name] = None

                # 정수형 처리
                elif field.type.type in ["int", "long"]:
                    try:
                        result[field.name] = int(value)
                    except ValueError:
                        result[field.name] = None

                # enum 처리 (delivery_type)
                elif field.type.type == "enum":
                    if value in field.type.symbols:
                        result[field.name] = value
                    else:
                        result[field.name] = None

                else:
                    result[field.name] = value

            logger.debug("Successfully converted Redis hash data")
            return result

        except Exception as e:
            logger.error(f"Error converting Redis hash to Avro format: {str(e)}")
            raise

    def validate_data(self, data: Dict) -> bool:
        """데이터 유효성 검증"""
        try:
            logger.debug(f"Validating data for DPS: {data.get('dps')}")

            # required 필드 검증
            required_fields = ['department', 'delivery_type', 'dps']
            for field in required_fields:
                if field not in data or data[field] is None:
                    logger.warning(f"Required field missing: {field}")
                    return False

            # delivery_type enum 검증
            if data['delivery_type'] not in ['delivery', 'return']:
                logger.warning(f"Invalid delivery_type: {data['delivery_type']}")
                return False

            # timestamp 필드 검증
            timestamp_fields = ['eta', 'depart_time', 'completed_time']
            for field in timestamp_fields:
                value = data.get(field)
                if value is not None:
                    if not isinstance(value, (int, float, datetime)):
                        logger.warning(f"Invalid timestamp format for {field}: {value}")
                        return False

            logger.debug("Data validation successful")
            return True

        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            return False