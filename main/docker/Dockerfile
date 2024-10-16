# Python 3.10을 기반으로 하는 경량 이미지를 사용
FROM python:3.10-slim

# 작업 디렉토리를 /app으로 설정
WORKDIR /app

# 파이썬 패키지 설치에 필요한 requirements.txt 파일을 복사
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 기본 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg2 \
    default-jdk  # openjdk-11-jdk 대신 default-jdk 사용

# Selenium을 위한 Chrome WebDriver 및 Chrome 브라우저 설치
RUN apt-get install -y wget unzip && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install && \
    wget -q https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/

# Google API 인증을 위한 환경 변수 설정
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/oauth/google/credentials.json"

# 소스 코드와 OAuth 인증 폴더를 복사
COPY src /app/src
COPY oauth /app/oauth

# PySpark와 Kafka 연동을 위한 필수 JAR 파일을 다운로드 및 설치
RUN apt-get install -y curl && \
    mkdir -p /opt/spark/jars && \
    curl -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.3.0.jar \
        https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.3.0/spark-sql-kafka-0-10_2.12-3.3.0.jar && \
    curl -o /opt/spark/jars/kafka-clients-2.8.0.jar \
        https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.0/kafka-clients-2.8.0.jar && \
    curl -o /opt/spark/jars/jackson-databind-2.12.3.jar \
        https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/2.12.3/jackson-databind-2.12.3.jar

# Java 환경 변수 설정
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
ENV PATH $PATH:$JAVA_HOME/bin

# PySpark 실행을 위한 환경 변수 설정
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# 메인 실행 파일 설정
CMD ["python", "src/main.py"]
