import dash
from dash import html, dcc, Input, Output
from confluent_kafka import Consumer
from queue import Queue
import pandas as pd
import threading
import logging
from src.config.config_manager import ConfigManager
from src.collectors.gcp_data import save_to_gcs, fetch_sheet_data
from datetime import datetime, timedelta


config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

app = dash.Dash(__name__)
data_queue = Queue()


def create_kafka_consumer():
    consumer_config = {
        'bootstrap.servers': config.kafka.BOOTSTRAP_SERVERS,
        'group.id': 'dashboard-consumer-group',
        'auto.offset.reset': 'latest'
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe([config.kafka.TOPICS['dashboard_status']])
    return consumer


def consume_kafka_messages():
    consumer = create_kafka_consumer()
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Kafka Consumer 오류: {msg.error()}")
                continue

            message = msg.value().decode('utf-8')
            data_queue.put(message)
    except KeyboardInterrupt:
        logger.info("Kafka 메시지 소비를 중단합니다.")
    finally:
        consumer.close()


threading.Thread(target=consume_kafka_messages, daemon=True).start()

app.layout = html.Div([
    html.H1("실시간 Kafka 데이터 대시보드"),
    dcc.Interval(id="interval-component", interval=2000, n_intervals=0),
    html.Div(id="live-update-text")
])


@app.callback(Output("live-update-text", "children"), Input("interval-component", "n_intervals"))
def update_data(n):
    if not data_queue.empty():
        data = []
        while not data_queue.empty():
            data.append(data_queue.get())

        df = pd.DataFrame([eval(row) for row in data])
        return html.Div([
            html.H2("실시간 데이터"),
            dcc.Graph(
                figure={
                    "data": [{"x": df["Date"], "y": df["Status"], "type": "bar"}],
                    "layout": {"title": "Status 별 실시간 분포"}
                }
            )
        ])
    else:
        return "데이터가 없습니다."


@app.callback(Output("live-update-text", "children"), Input("sheet-refresh-button", "n_clicks"))
def refresh_sheet_data(n_clicks):
    if n_clicks:
        # Google Sheets 데이터 로드 후 GCS에 저장
        data = fetch_sheet_data()
        if not data.empty:
            timestamp = datetime.datetime.now().strftime("%y%m%d-%H%M")
            file_name = f"data_{timestamp}.csv"
            save_to_gcs(data, file_name)
            return f"Google Sheets 데이터가 {file_name}으로 GCS에 저장되었습니다."
        else:
            return "Google Sheets에서 데이터를 가져올 수 없습니다."


if __name__ == "__main__":
    app.run_server(debug=True)
