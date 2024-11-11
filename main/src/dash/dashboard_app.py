import dash
from dash import html, dcc, Input, Output
import pandas as pd
import requests
from src.config.config_manager import ConfigManager

GCSConfig = ConfigManager().gcs

file_name = ConfigManager.file_name
cloud_end_point = GCSConfig.cloud_end_point

# Dash 앱 초기화
app = dash.Dash(__name__)


# GCS 데이터 로드 함수
def load_gcs_data():
    client = GCSConfig.get_client()
    bucket = client.bucket(GCSConfig.BUCKET_NAME)
    blob = bucket.blob(file_name)

    data = blob.download_as_text()
    df = pd.read_csv(pd.compat.StringIO(data))
    return df


# 레이아웃 정의
app.layout = html.Div([
    html.H1("GCS 데이터 및 Cloud Run 트리거"),
    html.Button("Cloud Run 트리거", id="trigger-button", n_clicks=0),
    html.Div(id="output-message"),
    dcc.Store(id="gcs-data")
])


# 버튼 클릭 시 Cloud Run 호출
@app.callback(
    Output("output-message", "children"),
    Input("trigger-button", "n_clicks")
)
def trigger_cloud_run(n_clicks):
    if n_clicks > 0:
        url = cloud_end_point
        response = requests.post(url)
        return f"Cloud Run 응답 상태 코드: {response.status_code}"


# GCS 데이터 로드 및 테이블 출력
@app.callback(
    Output("gcs-data", "data"),
    Input("trigger-button", "n_clicks")
)
def display_gcs_data(n_clicks):
    df = load_gcs_data()
    return df.to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)
