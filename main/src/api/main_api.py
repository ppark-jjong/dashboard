from fastapi import FastAPI, HTTPException
from google.cloud import pubsub_v1, storage
from src.config.spark_config import SparkConfig
from src.config.gcp_config import GCPConfig
from src.config.logger import Logger
import json
from pathlib import Path

app = FastAPI()
logger = Logger.get_logger(__name__)


@app.post("/publish")
def publish_message(data: dict):
    # Pub/Sub에 메시지 발행
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
        message = json.dumps(data).encode("utf-8")
        future = publisher.publish(topic_path, message)
        message_id = future.result()
        logger.info(f"Published message ID: {message_id}")
        return {"status": "success", "message_id": message_id}
    except Exception as e:
        logger.error(f"Failed to publish message: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish message")


@app.get("/consume")
def consume_message():
    # Pub/Sub에서 메시지 수신 및 Spark 전달
    try:
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)

        def callback(message):
            logger.info(f"Received message: {message.data}")
            # 메시지를 Spark 작업으로 전달
            start_spark_job(json.loads(message.data))
            message.ack()

        subscriber.subscribe(subscription_path, callback=callback)
        return {"status": "success", "message": "Consuming messages from Pub/Sub"}
    except Exception as e:
        logger.error(f"Failed to consume messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to consume messages")


@app.post("/start_spark_job")
def start_spark_job(data: dict):
    # Spark 작업 시작
    try:
        spark = SparkConfig.get_instance()
        logger.info("Starting Spark job...")
        # 데이터 처리 로직 추가 (예: DataFrame 생성)
        df = spark.read.json(json.dumps(data))
        df.show()
        logger.info("Spark job completed.")
        return {"status": "success", "message": "Spark job completed"}
    except Exception as e:
        logger.error(f"Failed to start Spark job: {e}")
        raise HTTPException(status_code=500, detail="Failed to start Spark job")


@app.post("/upload_to_gcs")
def upload_to_gcs():
    # JSON 데이터를 GCS에 업로드
    try:
        if not DATA_PATH.exists():
            raise HTTPException(status_code=404, detail="Data file not found")
        gcs_client = GCSConfig.get_client()
        bucket = gcs_client.bucket(GCSConfig.BUCKET_NAME)
        blob = bucket.blob("data/data.json")
        blob.upload_from_filename(DATA_PATH)
        logger.info("Data uploaded to GCS.")
        return {"status": "success", "message": "Data uploaded to GCS"}
    except Exception as e:
        logger.error(f"Failed to upload to GCS: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload to GCS")


@app.get("/download_from_gcs")
def download_from_gcs():
    # GCS에서 데이터를 로컬로 다운로드
    try:
        gcs_client = GCSConfig.get_client()
        bucket = gcs_client.bucket(GCSConfig.BUCKET_NAME)
        blob = bucket.blob("data/data.json")
        blob.download_to_filename(DATA_PATH)
        logger.info("Data downloaded from GCS.")
        return {"status": "success", "message": "Data downloaded from GCS"}
    except Exception as e:
        logger.error(f"Failed to download from GCS: {e}")
        raise HTTPException(status_code=500, detail="Failed to download from GCS")


@app.get("/analyze_results")
def analyze_results():
    # GCS의 Spark 작업 결과 분석
    try:
        gcs_client = GCSConfig.get_client()
        bucket = gcs_client.bucket(GCSConfig.BUCKET_NAME)
        blob = bucket.blob("results/output.json")
        blob.download_to_filename("./data/results.json")
        with open("./data/results.json", "r") as file:
            data = json.load(file)
        logger.info("Analysis results retrieved.")
        return {"status": "success", "results": data}
    except Exception as e:
        logger.error(f"Failed to analyze results: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze results")
