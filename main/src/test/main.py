# main.py
import json
import logging
from dash import Dash, dcc, html
from dash.dependencies import Input, Output  # Dash 콜백을 위한 Input, Output 임포트
import pandas as pd  # 데이터 분석 라이브러리
from queue import Queue  # 실시간 데이터 처리를 위한 큐
from confluent_kafka import Consumer, KafkaError  # Kafka Consumer 관련 라이브러리
from src.collectors.google_sheets import fetch_sheet_data  # Google Sheets 데이터 수집 함수
from src.kafka.producer import create_kafka_producer, send_to_kafka  # Kafka 프로듀서 함수
from src.processors.realtime_data_processor import process_data
from src.utils.file_handler import save_to_gcs  # GCS에 데이터 저장 함수
from src.config.config_manager import ConfigManager  # 설정 관리 클래스
from datetime import datetime  # 날짜 및 시간 처리를 위한 라이브러리

# 설정 초기화
config = ConfigManager()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  # 로그 설정
logger = logging.getLogger(__name__)  # 로거 생성

# 실시간 데이터를 저장할 큐
message_queue = Queue()

# Dash 앱 초기화
app = Dash(__name__)

# Dash 레이아웃 설정
app.layout = html.Div([
    dcc.Graph(id='live-update-graph'),  # 실시간 그래프 컴포넌트
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # 1초마다 업데이트
])

# 실시간 데이터를 Dash에 업데이트
@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph_live(n):
    data = []  # 큐에서 데이터를 수집할 리스트
    while not message_queue.empty():
        record = message_queue.get()  # 큐에서 데이터를 가져옴
        data.append(record)  # 데이터를 리스트에 추가

    df = pd.DataFrame(data)  # 리스트를 데이터프레임으로 변환
    figure = {
        'data': [{'x': df['ETA'], 'y': df['Status'], 'type': 'scatter', 'name': '실시간 데이터'}],  # scatter plot 설정
        'layout': {'title': '실시간 배송 현황'}  # 그래프 제목 설정
    }
    return figure  # 업데이트된 그래프 반환

# Kafka 메시지를 수신하고 GCS 및 Dash에 데이터 제공
def consume_and_process_messages():
    consumer_config = {
        'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,  # Kafka 서버 주소 설정
        'group.id': 'delivery-status-group',  # Consumer 그룹 ID 설정
        'auto.offset.reset': 'earliest'  # 초기 오프셋 설정
    }
    consumer = Consumer(consumer_config)  # Kafka Consumer 생성
    consumer.subscribe([config.KAFKA_TOPICS['realtime_status']])  # 토픽 구독
    logger.info(f"'{config.KAFKA_TOPICS['realtime_status']}' 토픽에서 메시지를 수신합니다.")  # 토픽 수신 로그

    records = []  # 수신된 메시지 저장 리스트

    try:
        while True:
            msg = consumer.poll(timeout=1.0)  # 메시지를 1초 대기하며 수신
            if msg is None:  # 메시지가 없으면 계속
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info(f"토픽의 마지막 메시지에 도달했습니다: {msg.topic()} [{msg.partition()}]")  # 파티션 끝 로그
                else:
                    logger.error(f"Consumer 오류: {msg.error()}")  # 에러 로그
                continue

            message_value = msg.value().decode('utf-8')  # 메시지 값 디코딩
            message = json.loads(message_value)  # JSON으로 변환
            records.append(message)  # 수신된 메시지 추가

            if len(records) >= 10:  # 10개의 메시지가 누적되면 처리
                today_data, future_data = process_data(records)  # 오늘 및 미래 데이터 분리

                for record in today_data.to_dict(orient='records'):
                    message_queue.put(record)  # 실시간 큐에 기록 추가

                if not future_data.empty:  # 미래 데이터가 있으면
                    file_name = f"future_eta_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"  # 파일 이름 생성
                    save_to_gcs(future_data, config.GCS_BUCKET_NAME, file_name, config.SERVICE_ACCOUNT_FILE)  # GCS 저장

                records = []  # 기록 초기화
    except KeyboardInterrupt:
        logger.info("메시지 소비를 중단합니다.")  # 소비 중단 로그
    finally:
        consumer.close()  # Kafka Consumer 종료
        logger.info("Kafka Consumer 연결을 종료합니다.")  # 종료 로그

# Google Sheets 데이터를 수집하여 Kafka로 전송하고, Consumer를 통해 GCS와 Dash로 처리
def main():
    df = fetch_sheet_data()  # Google Sheets 데이터 수집
    if df is None or df.empty:
        logger.warning("Google Sheets에서 가져온 데이터가 비어 있습니다.")  # 데이터가 비어있으면 경고
        return

    producer = create_kafka_producer()  # Kafka Producer 생성
    send_to_kafka(producer, config.KAFKA_TOPICS['realtime_status'], df)  # 데이터를 Kafka로 전송

    consume_and_process_messages()  # Kafka Consumer 실행

if __name__ == '__main__':
    import threading  # 스레딩 모듈

    consumer_thread = threading.Thread(target=main)  # Kafka Consumer를 별도의 스레드에서 실행
    consumer_thread.start()  # 스레드 시작

    app.run_server(debug=True, host='0.0.0.0', port=8050)  # Dash 서버 실행
