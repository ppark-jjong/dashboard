# src/dash/dashboard_app.py
import dash
from dash import html, dcc, Input, Output
import pandas as pd
import threading
import json
import requests
from src.kafka.consumer import KafkaConsumerService, data_queue
from src.config.config_manager import ConfigManager

app = dash.Dash(__name__)
config = ConfigManager()
consumer_service = KafkaConsumerService()

# Kafka Consumer를 별도 쓰레드로 실행
threading.Thread(target=consumer_service.consume_messages, daemon=True).start()

app.layout = html.Div([
    html.H1("실시간 Kafka 데이터 대시보드"),
    dcc.Interval(id="interval-component", interval=2000, n_intervals=0),
    html.Button("Cloud Run Trigger", id="trigger-button", n_clicks=0),
    html.Div(id="output-message"),
    html.Div(id="live-update-text"),
    html.Div(id="gcs-data")
])

@app.callback(Output("live-update-text", "children"), Input("interval-component", "n_intervals"))
def update_data(n):
    if not data_queue.empty():
        data = []
        while not data_queue.empty():
            data.append(data_queue.get())
        df = pd.DataFrame([json.loads(row) for row in data])
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

# 버튼 클릭 시 Cloud Run 호출
@app.callback(
    Output("output-message", "children"),
    Input("trigger-button", "n_clicks")
)
def trigger_cloud_run(n_clicks):
    if n_clicks > 0:
        url = config.cloud_run.CLOUD_RUN_ENDPOINT
        response = requests.post(url)
        return f"Cloud Run 응답 상태 코드: {response.status_code}"

# GCS 데이터 로드 및 테이블 출력
@app.callback(
    Output("gcs-data", "children"),
    Input("trigger-button", "n_clicks")
)
def display_gcs_data(n_clicks):
    if n_clicks > 0:
        # 임시로 data.json 데이터를 불러오는 예시 로직
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
            return f"데이터 로드 오류: {str(e)}"

if __name__ == "__main__":
    app.run_server(debug=True)
