from flask import Flask, request, jsonify
import pandas as pd
from src.brokers.kafka.producer import create_kafka_producer, send_to_kafka
from src.config.config_manager import ConfigManager

app = Flask(__name__)
config = ConfigManager()


@app.route("/", methods=["POST"])
def kafka_stream(request):
    try:
        # 요청 데이터 수신 및 DataFrame 생성
        data = request.get_json()
        df = pd.DataFrame([data], columns=config.sheets.COLUMNS)

        # 데이터 전처리
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Timestamp 객체를 문자열로 변환
        df = df.astype(str)

        # Kafka로 데이터 전송
        producer = create_kafka_producer()
        topic = config.kafka.TOPICS['realtime_status']
        send_to_kafka(producer, topic, df)

        return jsonify({"status": "success", "message": "Data sent to Kafka"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
