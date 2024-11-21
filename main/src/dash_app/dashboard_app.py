import dash
from dash import html, dash_table
import pandas as pd
import threading

from dash.dependencies import Output
from src.kafka.consumer import KafkaConsumerService
from src.config.config_format import DashBoardConfig
from src.config.logger import Logger

logger = Logger.get_logger(__name__)

# 글로벌 변수
latest_data = pd.DataFrame(columns=DashBoardConfig.DASHBOARD_COLUMNS)
lock = threading.Lock()
consumer_service = KafkaConsumerService()

# Dash 애플리케이션 초기화
app = dash.Dash(__name__)

# Dash 레이아웃
app.layout = html.Div([
    html.H1("실시간 배송 현황", style={"textAlign": "center"}),
    dash_table.DataTable(
        id='live-table',
        columns=[{"name": col, "id": col} for col in DashBoardConfig.DASHBOARD_COLUMNS],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={'fontWeight': 'bold'}
    )
])


# Kafka 데이터를 읽고 테이블을 즉시 업데이트
def consume_kafka_data():
    global latest_data
    while True:
        today_data = consumer_service.consume_latest_data()
        if not today_data.empty:
            with lock:
                latest_data = pd.concat([latest_data, today_data], ignore_index=True)
                latest_data.drop_duplicates(subset=DashBoardConfig.DASHBOARD_COLUMNS, inplace=True)
                logger.info(f"dash 가 카프카 데이터 consume 완료")

                # 테이블 강제 갱신
                app.callback_map['live-table.data']['callback']()


# Kafka Consumer 스레드 실행
threading.Thread(target=consume_kafka_data, daemon=True).start()


# Dash 콜백
@app.callback(
    Output('live-table', 'data'),
    prevent_initial_call=True
)
#     새로운 데이터가 들어올 때 테이블을 최신화
def update_table():
    with lock:
        return latest_data.to_dict('records')


if __name__ == "__main__":
    app.run_server(debug=True)
