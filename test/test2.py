import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# UI/UX 색상 시스템 정의
COLORS = {
    'primary': '#1976D2',
    'success': '#2E7D32',
    'warning': '#ED6C02',
    'error': '#D32F2F',
    'company': '#F01818',
    'bg_primary': '#E3F2FD',
    'bg_success': '#E8F5E9',
    'bg_warning': '#FFF3E0',
    'bg_error': '#FFEBEE',
    'chart_complete': '#2E7D32',
    'chart_progress': '#ED6C02',
    'chart_total': '#1976D2',
    'active_tab': '#FFCDD2',  # 활성화된 탭 색상
}

# 데이터 생성 함수
def generate_delivery_data():
    return pd.DataFrame({
        'Department': ['hes', 'hes'],
        'Delivery': ['아무개', '가나다'],
        'DPS': [1234, 6578],
        'ETA': ['2024-06-12 13:00', '2024-06-12 17:00'],
        'SLA': ['4HR(24X7)', '4HR(24X7)'],
        'Address': ['기흥단지로 46 HL인재개발원', '경기도 화성시 삼성전자로 1-1 DSR동 C타워'],
        'Status': ['complete', 'shipping'],
        'Recipient': ['이태성', '강민서']
    })

def generate_driver_status():
    drivers = ['아무개', '가나다', '철수', '영희']
    statuses = ['배송중', '배송완료', '복귀중']
    return pd.DataFrame({
        '기사명': drivers,
        '현재상태': [random.choice(statuses) for _ in drivers],
        '담당지역': ['기흥', '화성', '수원', '용인'],
        '오늘배송건수': [random.randint(5, 20) for _ in drivers],
        '완료건수': [random.randint(0, 15) for _ in drivers],
        '예상복귀시간': [
            (datetime.now() + timedelta(minutes=random.randint(10, 60))).strftime('%H:%M')
            for _ in drivers
        ]
    })

# Dash 앱 초기화
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label="배송 현황", value='tab-1', style={'backgroundColor': COLORS['bg_primary']}),
        dcc.Tab(label="기사 현황", value='tab-2', style={'backgroundColor': COLORS['bg_primary']}),
    ], colors={"border": COLORS['primary'], "primary": COLORS['active_tab'], "background": COLORS['bg_primary']}),
    html.Div(id='tabs-content'),
    # 모달 컴포넌트
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("상세 정보")),
            dbc.ModalBody(id="modal-body"),
            dbc.ModalFooter(
                dbc.Button("닫기", id="close-modal", color="primary", className="ms-auto")
            ),
        ],
        id="detail-modal",
        size="lg",
    ),
], fluid=True, style={'maxWidth': '80%', 'margin': '0 auto'})

# 탭 내용 콜백
@callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_tab_content(tab_name):
    if tab_name == 'tab-1':
        return html.Div([
            html.H1("배송 현황", className="text-center my-4"),
            dbc.Table(id='delivery-table', bordered=True, hover=True, responsive=True),
        ])
    elif tab_name == 'tab-2':
        return html.Div([
            html.H1("기사 현황", className="text-center my-4"),
            dbc.Table(id='driver-table', bordered=True, hover=True, responsive=True),
        ])

# 테이블 데이터 클릭 시 모달 표시
@callback(
    Output("detail-modal", "is_open"),
    Output("modal-body", "children"),
    Input({'type': 'row', 'index': dash.ALL}, 'n_clicks'),
    State('tabs', 'value'),
    prevent_initial_call=True
)
def display_modal(n_clicks, tab_name):
    if not n_clicks:
        return False, None
    if tab_name == 'tab-1':
        return True, "배송 현황 상세 정보"
    elif tab_name == 'tab-2':
        return True, "기사 현황 상세 정보"
    return False, None

if __name__ == '__main__':
    app.run_server(debug=True)
