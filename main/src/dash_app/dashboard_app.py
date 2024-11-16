import dash
from dash import html
import pandas as pd
import threading
import json
import logging
from dash.dependencies import Output
from src.kafka.consumer import KafkaConsumerService
from dash import dash_table

# Logging 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Dash 애플리케이션 인스턴스 생성
app = dash.Dash(__name__)
latest_data = pd.DataFrame(columns=["DPS", "Delivery", "ETA", "Status", "Billed Distance"])  # 전체 데이터를 저장할 DataFrame
consumer_service = KafkaConsumerService(topic="dashboard_status")  # Kafka 소비자 인스턴스 생성

# Dash 레이아웃 정의
app.layout = html.Div([
    html.H1("실시간 배송 현황"),
    html.Div(id="live-update-text")
])

# 실시간 데이터 테이블 생성 함수
def generate_table(dataframe):
    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        data=dataframe.to_dict("records"),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={'fontWeight': 'bold'}
    )

# Kafka 메시지를 소비하여 DataFrame에 추가
def consume_kafka_data():
    global latest_data
    while True:
        today_data = consumer_service.consume_today_data()
        if not today_data.empty:
            latest_data = pd.concat([latest_data, today_data], ignore_index=True)
            logger.info("오늘 데이터 업데이트됨:\n%s", latest_data)

            # Dash 레이아웃 업데이트
            app.layout['live-update-text'].children = generate_table(latest_data)

# Kafka Consumer를 별도 스레드에서 실행하여 데이터 소비
threading.Thread(target=consume_kafka_data, daemon=True).start()

if __name__ == "__main__":
    app.run_server(debug=True)
