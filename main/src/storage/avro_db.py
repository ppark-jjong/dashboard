from datetime import datetime, date
from typing import Dict, Optional
from avro_base import AvroProcessor


class DBProcessor(AvroProcessor):
    """DB 데이터 처리를 위한 클래스"""

    def to_db_format(self, data: Dict) -> Dict:
        """Avro 데이터를 DB 포맷으로 변환"""
        result = {}
        for field in self.schema.fields:
            value = data.get(field.name)

            # timestamp-millis를 datetime으로 변환
            if (field.type.type == "long" and
                    field.type.get_prop("logicalType") == "timestamp-millis" and
                    value is not None):
                result[field.name] = datetime.fromtimestamp(value / 1000)

            # date 타입 처리
            elif (field.type.type == "int" and
                  field.type.get_prop("logicalType") == "date" and
                  value is not None):
                result[field.name] = date.fromtimestamp(value * 86400)

            else:
                result[field.name] = value

        return result

    def from_db_format(self, data: Dict) -> Dict:
        """DB 데이터를 Avro 포맷으로 변환"""
        result = {}
        for field in self.schema.fields:
            value = data.get(field.name)

            if isinstance(value, datetime):
                result[field.name] = int(value.timestamp() * 1000)
            elif isinstance(value, date):
                result[field.name] = (value - date(1970, 1, 1)).days
            else:
                result[field.name] = value

        return result