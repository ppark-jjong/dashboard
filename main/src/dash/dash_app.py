# src/dash_app.py
import json
import logging
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from confluent_kafka import Consumer, KafkaError
from collections import deque
import plotly.express as px

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Dash 앱 초기화
app = Dash(__name__)
app.title = "실시간 배송 현황 대시보드"

# Kafka 설정
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'realtime_status'
MAX_DATA_POINTS = 100  # 한 번에 보여줄 최대 데이터 포인트 개수

# 데이터를 저장할 큐 초기화
data_queue = deque(maxlen=MAX_DATA_POINTS)


# Kafka Consumer 생성
def create_kafka_consumer():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'dash-consumer-group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([KAFKA_TOPIC])
    return consumer


# Kafka로부터 데이터를 수신하고 큐에 저장
def consume_kafka_messages(consumer):
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info(f"토픽의 마지막 메시지에 도달했습니다: {msg.topic()} [{msg.partition()}]")
                else:
                    logger.error(f"Consumer 오류: {msg.error()}")
                continue

            # 메시지를 디코딩하고 큐에 추가
            message_value = json.loads(msg.value().decode('utf-8'))
            data_queue.append(message_value)
            logger.info(f"수신한 메시지: {message_value}")

    except Exception as e:
        logger.error(f"Kafka 메시지 수신 중 오류 발생: {e}")


# Consumer 초기화
consumer = create_kafka_consumer()

# Dash 레이아웃 설정
app.layout = html.Div([
    html.H1("실시간 배송 현황 대시보드"),
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5 * 1000,  # 5초마다 데이터 업데이트
        n_intervals=0
    )
])


# 그래프 업데이트 콜백 함수
@app.callback(
    Output('live-update-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph_live(n_intervals):
    # Kafka 메시지 수신
    consume_kafka_messages(consumer)

    if not data_queue:
        return {}

    # 큐에서 데이터를 가져와 DataFrame 생성
    df = pd.DataFrame(list(data_queue))
    df['Date(접수일)'] = pd.to_datetime(df['Date(접수일)'])

    # 예시: 상태별 배송 건수 그래프
    fig = px.bar(df, x='Date(접수일)', y='Status', color='Status',
                 title="실시간 배송 상태별 현황",
                 labels={'Status': '배송 상태', 'Date(접수일)': '접수일'})

    return fig


# Dash 앱 실행
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
