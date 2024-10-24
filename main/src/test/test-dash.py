# main.py
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px  # 그래프 생성을 위한 plotly 라이브러리

# 간단한 데이터 생성
df = pd.DataFrame({
    "Category": ["A", "B", "C", "D"],
    "Value": [4, 3, 2, 5]
})

# Dash 앱 초기화
app = Dash(__name__)

# Dash 레이아웃 설정
app.layout = html.Div([
    html.H1("Simple Dash App Example"),  # 제목
    dcc.Graph(id='bar-chart'),  # 그래프 컴포넌트
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # 1초마다 업데이트
])

# 막대 그래프를 생성하여 반환
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    # 그래프 생성
    fig = px.bar(df, x="Category", y="Value", title="Simple Bar Chart")
    return fig

# Dash 서버 실행
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8051)
