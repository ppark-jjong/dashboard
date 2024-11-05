
# Python 3.10을 기반으로 하는 경량 이미지
FROM python:3.10-slim

# 작업 디렉토리를 /app으로 설정
WORKDIR /app

# Python 경로를 설정하여 src 디렉토리를 인식하도록 함
ENV PYTHONPATH=/app
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/oauth/google/credentials.json"
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# 의존성 설치 - requirements.txt 복사 및 설치
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 필수 패키지 설치 및 Chrome WebDriver와 Chrome 브라우저 설치
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg2 default-jdk && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install && \
    wget -q https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/local/bin && \
    rm -f google-chrome-stable_current_amd64.deb chromedriver_linux64.zip

# 소스 코드와 OAuth 인증 폴더를 복사
COPY ./src /app/src
COPY ./secrets /app/secrets

# PySpark와 Kafka 연동을 위한 필수 JAR 파일 다운로드
RUN mkdir -p /opt/spark/jars && \
    curl -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.3.0.jar \
        https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.3.0/spark-sql-kafka-0-10_2.12-3.3.0.jar && \
    curl -o /opt/spark/jars/kafka-clients-2.8.0.jar \
        https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.0/kafka-clients-2.8.0.jar && \
    curl -o /opt/spark/jars/jackson-databind-2.12.3.jar \
        https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/2.12.3/jackson-databind-2.12.3.jar

# FastAPI와 Dash 웹 애플리케이션 포트 노출
EXPOSE 8080
EXPOSE 8050

# Webhook 및 Dash 서비스 실행을 위한 기본 명령
CMD ["python", "src/test/test-dash.py"]
