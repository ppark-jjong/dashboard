from datetime import datetime, date
from typing import Dict, Optional
from avro_base import AvroProcessor


class RedisProcessor(AvroProcessor):
    """Redis 데이터 처리를 위한 클래스"""

    def to_redis_hash(self, data: Dict) -> Dict:
        """Avro 데이터를 Redis hash 형식으로 변환"""
        result = {}
        for field in self.schema.fields:
            value = data.get(field.name)

            if value is None:
                result[field.name] = ""
            elif isinstance(value, (datetime, date)):
                result[field.name] = str(int(value.timestamp() * 1000))
            elif isinstance(value, (int, float)):
                result[field.name] = str(value)
            else:
                result[field.name] = str(value)

        # 캐시 메타데이터 추가
        result['cache_timestamp'] = str(int(datetime.now().timestamp() * 1000))

        return result

    def from_redis_hash(self, hash_data: Dict) -> Dict:
        """Redis hash 데이터를 Avro 형식으로 변환"""
        result = {}
        for field in self.schema.fields:
            value = hash_data.get(field.name, "")

            if value == "":
                result[field.name] = None
            elif field.type.type == "long" and field.type.get_prop("logicalType") == "timestamp-millis":
                result[field.name] = int(value) if value else None
            elif field.type.type == "int":
                result[field.name] = int(value) if value else None
            elif field.type.type == "enum":
                result[field.name] = value if value in field.type.symbols else None
            else:
                result[field.name] = value

        return result

    def validate_data(self, data: Dict) -> bool:
        """데이터 유효성 검증"""
        try:
            # 직렬화/역직렬화를 통한 스키마 검증
            avro_bytes = self.serialize(data)
            self.deserialize(avro_bytes)
            return True
        except Exception:
            return False