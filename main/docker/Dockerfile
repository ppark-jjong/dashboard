<<<<<<< HEAD
FROM python:3.9-slim-buster

ENV SPARK_VERSION=3.5.3
ENV SPARK_HOME=/opt/spark
ENV PYSPARK_PYTHON=python3
ENV PYTHONHASHSEED=1
ENV PATH=$PATH:${SPARK_HOME}/bin

# 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-11-jre-headless \
        curl \
        && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip3 install --upgrade pip

# Python 패키지 설치
COPY ../config/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Spark without Hadoop 다운로드 및 설치
RUN curl -O https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-without-hadoop.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-without-hadoop.tgz && \
    mv spark-${SPARK_VERSION}-bin-without-hadoop ${SPARK_HOME} && \
    rm spark-${SPARK_VERSION}-bin-without-hadoop.tgz

# jars 폴더의 모든 JAR 파일을 Spark의 jars 디렉토리로 복사
COPY ../jars/*.jar ${SPARK_HOME}/jars/
=======
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
>>>>>>> origin/main

WORKDIR /app

<<<<<<< HEAD
COPY ../src /app/src
COPY ../proto /app/proto
COPY ../oauth /app/oauth

CMD ["python3", "/app/src/main.py"]
=======
# 전체 프로젝트 파일을 복사합니다.
COPY . /app

ENV PYTHONPATH="/app/src:/app/proto"

# OAuth 인증 정보 복사 (필요시 추가)
COPY oauth/google/credentials.json /app/oauth/google/credentials.json

# Command to run the main Python script
CMD ["python3", "/app/src/main.py"]
>>>>>>> origin/main
