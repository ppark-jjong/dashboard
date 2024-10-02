# Base image for Python and Spark
FROM openjdk:8-jdk-slim

# 기본적으로 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    bash && \
    pip3 install --upgrade pip

# Install PySpark
RUN pip3 install pyspark==3.4.0

# Install Kafka Python client, Protobuf, and Google API libraries
RUN pip3 install \
    confluent-kafka \
    protobuf \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib \
    pandas

# Set the working directory
WORKDIR /app

# 전체 프로젝트 파일을 복사합니다.
COPY . /app

ENV PYTHONPATH="/app/src:/app/proto"

# OAuth 인증 정보 복사 (필요시 추가)
COPY oauth/google/credentials.json /app/oauth/google/credentials.json

# Command to run the main Python script
CMD ["python3", "/app/src/main.py"]
