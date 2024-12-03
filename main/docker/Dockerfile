# Python 3.10을 기반으로 하는 경량 이미지
FROM python:3.10-slim

# 작업 디렉토리를 /app으로 설정
WORKDIR /app

# Python 경로를 설정하여 src 디렉토리를 인식하도록 함
ENV PYTHONPATH=/app/src
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# 의존성 설치 - requirements.txt 복사 및 설치
COPY ../requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드와 데이터를 복사 (빌드 시점)
COPY ../src /app/src
COPY ../data /app/data

# PySpark와 Kafka 연동을 위한 필수 JAR 파일 다운로드
RUN mkdir -p /opt/spark/jars && \
    curl -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.3.0.jar \
        https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.3.0/spark-sql-kafka-0-10_2.12-3.3.0.jar && \
    curl -o /opt/spark/jars/jackson-databind-2.12.3.jar \
        https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/2.12.3/jackson-databind-2.12.3.jar

# 기본 명령어 설정
CMD ["spark-submit", "/app/src/processors/process_data.py"]
