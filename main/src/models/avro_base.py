# src/models/avro_base.py
import os
from datetime import datetime, date
from typing import Dict, Optional
import avro.schema
from avro.io import DatumWriter, DatumReader, BinaryEncoder, BinaryDecoder
from io import BytesIO


class AvroProcessor:
    """Avro 스키마 처리를 위한 기본 클래스"""

    def __init__(self, schema_path: str):
        self.schema = self.load_schema(schema_path)

    @staticmethod
    def load_schema(schema_path: str) -> avro.schema.Schema:
        """스키마 파일 로드"""
        with open(schema_path, 'r') as f:
            return avro.schema.parse(f.read())

    def serialize(self, data: Dict) -> bytes:
        """데이터를 Avro 형식으로 직렬화"""
        writer = DatumWriter(self.schema)
        bytes_writer = BytesIO()
        encoder = BinaryEncoder(bytes_writer)
        writer.write(data, encoder)
        return bytes_writer.getvalue()

    def deserialize(self, avro_bytes: bytes) -> Dict:
        """Avro 바이트를 데이터로 역직렬화"""
        reader = DatumReader(self.schema)
        bytes_reader = BytesIO(avro_bytes)
        decoder = BinaryDecoder(bytes_reader)
        return reader.read(decoder)