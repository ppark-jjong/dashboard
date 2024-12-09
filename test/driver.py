import dash
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd

# 정적 데이터
driver_data = pd.DataFrame([
    {'기사명': '김철수', '현재상태': '배송완료', '담당지역': '서울', '오늘배송건수': 15, '완료건수': 12, '예상복귀시간': '17:00'},
    {'기사명': '박영수', '현재상태': '배송중', '담당지역': '수원', '오늘배송건수': 10, '완료건수': 8, '예상복귀시간': '18:30'}
])

# Dash 앱 초기화
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 레이아웃
app.layout = dbc.Container([
    html.H1("기사 현황 시트", className="text-center my-4"),
    dbc.Table.from_dataframe(driver_data, bordered=True, hover=True, responsive=True)
], fluid=True, style={'maxWidth': '90%'})

if __name__ == '__main__':
    app.run_server(debug=True)
