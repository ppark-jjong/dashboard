import dash
from dash import html, dcc, Input, Output
import pandas as pd
import threading
import json
import requests
from queue import Queue, Empty
import logging
from src.kafka.consumer import KafkaConsumerService
from src.config.config_manager import ConfigManager

# Logging 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Dash 애플리케이션 인스턴스 생성
app = dash.Dash(__name__)
config = ConfigManager()
data_queue = Queue()
consumer_service = KafkaConsumerService(topic="dashboard_status")

# Kafka Consumer에서 데이터를 소비하여 메모리 큐에 저장
def consume_kafka_messages():
    try:
        while True:
            # Kafka에서 데이터를 소비하여 큐에 추가
            message = consumer_service.data_queue.get(timeout=1)
            if message:
                logger.info("Queue에 데이터 추가")
    except Empty:
        pass

# Kafka Consumer를 별도 스레드에서 실행하여 데이터 소비
threading.Thread(target=consumer_service.consume_messages, daemon=True).start()
threading.Thread(target=consume_kafka_messages, daemon=True).start()


# Dash 레이아웃 정의
app.layout = html.Div([
    html.H1("실시간 Kafka 데이터 대시보드"),
    dcc.Interval(id="interval-component", interval=2000, n_intervals=0),
    html.Button("Cloud Run Trigger", id="trigger-button", n_clicks=0),
    html.Div(id="output-message"),
    html.Div(id="live-update-text"),
    html.Div(id="gcs-data")
])


# 실시간 데이터 업데이트 콜백 함수
@app.callback(Output("live-update-text", "children"), Input("interval-component", "n_intervals"))
def update_data(n):
    data = []
    try:
        # 큐에서 데이터를 꺼내 DataFrame을 구성
        while True:
            data.append(data_queue.get_nowait())
    except Empty:
        pass

    if data:
        # 수신된 JSON 데이터 리스트를 DataFrame으로 변환
        df = pd.DataFrame([json.loads(row) for row in data])

        # 그래프 시각화 (Date와 Status 기반으로 예시)
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
        # 데이터가 없을 경우 기본 메세지와 빈 차트
        return html.Div([
            html.H2("실시간 데이터 없음"),
            dcc.Graph(figure={"data": [], "layout": {"title": "데이터가 없습니다"}})
        ])


# Cloud Run 트리거 버튼 클릭 콜백 함수
@app.callback(
    Output("output-message", "children"),
    Input("trigger-button", "n_clicks")
)
def trigger_cloud_run(n_clicks):
    if n_clicks > 0:
        try:
            url = config.cloud_run.CLOUD_RUN_ENDPOINT
            response = requests.post(url)
            return f"Cloud Run 응답 상태 코드: {response.status_code}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Cloud Run 트리거 오류: {e}")
            return "Cloud Run 트리거 실패"


# GCS 데이터 로드 콜백 함수
@app.callback(
    Output("gcs-data", "children"),
    Input("trigger-button", "n_clicks")
)
def display_gcs_data(n_clicks):
    if n_clicks > 0:
        try:
            with open("data/data.json", "r") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            return html.Div([
                html.H2("GCS 데이터"),
                html.Table([
                               html.Tr([html.Th(col) for col in df.columns])] +
                           [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(min(len(df), 10))]
                           )
            ])
        except Exception as e:
            logger.error(f"GCS 데이터 로드 오류: {e}")
            return f"데이터 로드 오류: {str(e)}"


if __name__ == "__main__":
    app.run_server(debug=True)
