import dash
from dash import html, dcc
import pandas as pd
import threading
import json
import logging
from queue import Queue
from dash.dependencies import Input, Output
from src.kafka.consumer import KafkaConsumerService
from src.config.config_manager import ConfigManager
from dash import dash_table

# Logging 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Dash 애플리케이션 인스턴스 생성
app = dash.Dash(__name__)
config = ConfigManager()
data_queue = Queue()  # 전역 큐 인스턴스
consumer_service = KafkaConsumerService(topic="dashboard_status")  # Kafka 소비자 인스턴스 생성
latest_data = pd.DataFrame(columns=["DPS", "Delivery", "ETA", "Status", "Billed Distance"])  # 전체 데이터를 저장할 DataFrame

# 새로운 데이터 플래그 설정
new_data_flag = False


# Kafka 메시지를 소비하여 Queue에 추가 및 Dash 업데이트 트리거
def consume_kafka_data():
    global new_data_flag
    while True:
        consumer_service.consume_messages(max_records=5)

        # 수신된 메시지 크기 로그 확인
        queue_size = data_queue.qsize()
        logger.info("Queue에 새로운 데이터 추가됨, 현재 Queue 크기: %d", queue_size)

        # new_data_flag 설정
        new_data_flag = queue_size > 0


# Kafka Consumer를 별도 스레드에서 실행하여 데이터 소비
threading.Thread(target=consume_kafka_data, daemon=True).start()

# Dash 레이아웃 정의
app.layout = html.Div([
    html.H1("실시간 Kafka 데이터 대시보드"),
    dcc.Interval(id="interval-component", interval=2000, n_intervals=0),
    html.Div(id="live-update-text")
])


# 실시간 데이터 테이블 업데이트 함수
@app.callback(Output("live-update-text", "children"), Input("interval-component", "n_intervals"))
def update_data(n_intervals):
    global latest_data, new_data_flag
    logger.info("update_data 함수 호출됨 - new_data_flag: %s, Queue 크기: %d", new_data_flag, data_queue.qsize())

    # 새로운 데이터가 없으면 업데이트 중단
    if not new_data_flag:
        return html.Div([
            html.H2("실시간 데이터 없음")
        ])

    # Queue에서 모든 데이터를 가져와 DataFrame으로 추가
    data = []
    while not data_queue.empty():
        data.append(data_queue.get())

    if data:
        df = pd.DataFrame([json.loads(row) for row in data])

        # bool 컬럼 변환
        if 'Picked' in df.columns:
            df['Picked'] = df['Picked'].astype(bool)
        if 'Shipped' in df.columns:
            df['Shipped'] = df['Shipped'].astype(bool)
        if 'POD' in df.columns:
            df['POD'] = df['POD'].astype(bool)

        # 기존 데이터에 새로운 데이터 추가
        latest_data = pd.concat([latest_data, df], ignore_index=True)
        logger.info("DataFrame 업데이트됨:\n%s", latest_data)

    # 새로운 데이터가 처리되었으므로 플래그 초기화
    new_data_flag = False

    # 필요한 컬럼만 필터링하여 테이블 형식으로 표시
    if all(col in latest_data.columns for col in ["DPS", "Delivery", "ETA", "Status", "Billed Distance"]):
        table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in ["DPS", "Delivery", "ETA", "Status", "Billed Distance"]],
            data=latest_data[["DPS", "Delivery", "ETA", "Status", "Billed Distance"]].to_dict("records"),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_header={'fontWeight': 'bold'}
        )
        logger.info("DataTable 업데이트됨")
        return html.Div([
            html.H2("실시간 데이터 테이블"),
            table
        ])
    else:
        logger.warning("DataFrame에 필요한 컬럼이 없습니다.")
        return html.Div([
            html.H2("유효한 데이터가 없습니다")
        ])


if __name__ == "__main__":
    app.run_server(debug=True)
