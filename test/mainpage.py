import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

# 색상 정의
COLORS = {
    'primary': '#1976D2',
    'success': '#2E7D32',
    'warning': '#ED6C02',
    'error': '#D32F2F',
}

# 정적 데이터
delivery_data = pd.DataFrame([
    {'Department': 'Logistics', 'Delivery': '김철수', 'DPS': 1010, 'ETA': '2024-12-10 14:00',
     'SLA': '4HR', 'Address': '서울특별시 강남구', 'Status': '완료', 'Recipient': '이영희'},
    {'Department': 'Logistics', 'Delivery': '박영수', 'DPS': 2020, 'ETA': '2024-12-10 16:00',
     'SLA': '6HR', 'Address': '경기도 수원시', 'Status': '진행중', 'Recipient': '최수진'},
    {'Department': 'Logistics', 'Delivery': '최민수', 'DPS': 3030, 'ETA': '2024-12-10 18:00',
     'SLA': '12HR', 'Address': '부산광역시', 'Status': '대기', 'Recipient': '김영희'}
])

driver_data = pd.DataFrame([
    {'기사명': '김철수', '현재상태': '배송완료', '담당지역': '서울', '오늘배송건수': 15, '완료건수': 12, '예상복귀시간': '17:00'},
    {'기사명': '박영수', '현재상태': '배송중', '담당지역': '수원', '오늘배송건수': 10, '완료건수': 8, '예상복귀시간': '18:30'}
])

# 원형 그래프 생성
def create_delivery_pie():
    summary = delivery_data['Status'].value_counts()
    fig = go.Figure(data=[go.Pie(
        labels=summary.index,
        values=summary.values,
        hole=0.3,
        marker=dict(colors=[COLORS['success'], COLORS['warning'], COLORS['primary']])
    )])
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200)
    return fig

# Dash 앱 초기화
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 레이아웃
app.layout = dbc.Container([
    html.H1("ERP 시스템 대시보드", className="text-center my-4"),
    dbc.Tabs([
        dbc.Tab(label="Main 시트", tab_id="main-sheet"),
        dbc.Tab(label="배송 현황 시트", tab_id="delivery-sheet"),
        dbc.Tab(label="기사 현황 시트", tab_id="driver-sheet")
    ], id="tabs", active_tab="main-sheet", className="mb-4"),
    html.Div(id="tab-content")
], fluid=True, style={'maxWidth': '90%'})

# 콜백: 탭 변경 시 내용 업데이트
@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'active_tab')]
)
def render_tab_content(active_tab):
    if active_tab == "main-sheet":
        return render_main_sheet()
    elif active_tab == "delivery-sheet":
        return render_delivery_sheet()
    elif active_tab == "driver-sheet":
        return render_driver_sheet()
    return html.Div("선택된 탭이 없습니다.", className="text-center my-4")

# Main 시트 렌더링
def render_main_sheet():
    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("배송 현황"),
            dbc.CardBody([
                dcc.Graph(figure=create_delivery_pie(), config={'displayModeBar': False}),
                html.Ul([
                    html.Li(f"{status}: {count}건")
                    for status, count in delivery_data['Status'].value_counts().items()
                ])
            ])
        ]), width=6),
        dbc.Col(dbc.Card([
            dbc.CardHeader("기사 현황"),
            dbc.CardBody([
                html.Ul([
                    html.Li(f"{row['기사명']}: 배송 {row['오늘배송건수']}건, 완료 {row['완료건수']}건")
                    for _, row in driver_data.iterrows()
                ])
            ])
        ]), width=6),
    ])

# 배송 현황 시트 렌더링
def render_delivery_sheet():
    summary = delivery_data['Status'].value_counts().to_dict()
    header = html.Thead(html.Tr([html.Th(col) for col in delivery_data.columns]))
    rows = [html.Tr([
        html.Td(row[col]) for col in delivery_data.columns
    ], id=f"row-{i}") for i, row in delivery_data.iterrows()]
    body = html.Tbody(rows)

    return html.Div([
        html.Div([
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("배송 건", className="card-title"),
                        html.H2(f"{summary.get('대기', 0) + summary.get('진행중', 0) + summary.get('완료', 0)}건")
                    ])
                ]), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("배송 중", className="card-title"),
                        html.H2(f"{summary.get('진행중', 0)}건", style={'color': COLORS['warning']})
                    ])
                ]), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("배송 완료", className="card-title"),
                        html.H2(f"{summary.get('완료', 0)}건", style={'color': COLORS['success']})
                    ])
                ]), width=4),
            ]),
            dbc.Button("새로고침", id="refresh-btn", color="primary", className="mt-3")
        ]),
        html.H2("배송 상세 데이터", className="text-center my-4"),
        dbc.Table([header, body], bordered=True, hover=True, responsive=True, id='delivery-table'),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("배송 상세 정보")),
            dbc.ModalBody(id="modal-body"),
            dbc.ModalFooter(dbc.Button("닫기", id="close-modal", className="ms-auto", n_clicks=0))
        ], id="detail-modal", size="lg")
    ])

# 기사 현황 시트 렌더링
def render_driver_sheet():
    header = html.Thead(html.Tr([html.Th(col) for col in driver_data.columns]))
    rows = [html.Tr([
        html.Td(row[col]) for col in driver_data.columns
    ]) for _, row in driver_data.iterrows()]
    body = html.Tbody(rows)

    return html.Div([
        html.H2("기사 현황", className="text-center my-4"),
        dbc.Table([header, body], bordered=True, hover=True, responsive=True)
    ])

# 배송 테이블 행 클릭 시 모달 표시
@app.callback(
    [Output("detail-modal", "is_open"),
     Output("modal-body", "children")],
    [Input({'type': 'row', 'index': dash.ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def show_modal(n_clicks):
    if not n_clicks:
        return False, None
    return True, "선택한 배송의 상세 정보"

if __name__ == '__main__':
    app.run_server(debug=True)
