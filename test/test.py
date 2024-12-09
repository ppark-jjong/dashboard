import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
import random


# 배송 상태 샘플 데이터 생성 함수
def generate_delivery_data():
    return pd.DataFrame({
        'Department': ['hes', 'hes'],
        'Delivery': ['아무개', '가나다'],
        'DPS': [1234, 6578],
        'ETA': ['2024-06-12 13:00', '2024-06-12 17:00'],
        'SLA': ['4HR(24X7)', '4HR(24X7)'],
        'Address': ['기흥단지로 46 HL인재개발원', '경기도 화성시 삼성전자로 1-1 DSR동 C타워'],
        'Status': ['complete', 'shipping'],
        'Pickup': ['O', 'O'],
        'Delivered': ['O', ''],
        'ZipCode': [17086, 18448],
        'Recipient': ['이태성', '강민서'],
        'DepartTime': ['2024-12-06 12:47', '2024-12-06 12:47'],
        'ArrivalTime': ['2024-12-06 12:45', '2024-12-06 12:45']
    })


# 기사 상황 데이터 생성 함수
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

# 레이아웃 설정
app.layout = dbc.Container([
    dbc.Tabs([
        dbc.Tab(label="배송 현황", children=[
            html.Div([
                html.H1("실시간 배송 현황", className="text-center my-4"),

                # 통계 카드들
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H4("전체 배송건수", className="card-title"),
                            html.H2(id="total-deliveries", className="card-text")
                        ])
                    ]), width=3),
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H4("진행중", className="card-title"),
                            html.H2(id="in-progress", className="card-text")
                        ])
                    ]), width=3),
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H4("완료", className="card-title"),
                            html.H2(id="completed", className="card-text")
                        ])
                    ]), width=3),
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H4("SLA 준수율", className="card-title"),
                            html.H2(id="sla-rate", className="card-text")
                        ])
                    ]), width=3),
                ], className="mb-4"),

                # 새로고침 버튼
                html.Div([
                    dbc.Button("새로고침", id="refresh-button", color="primary", className="mb-3")
                ], style={'textAlign': 'right'}),

                # 메인 테이블
                dbc.Table(id='delivery-table', bordered=True, hover=True, responsive=True),

                # 상세 정보 모달
                dbc.Modal([
                    dbc.ModalHeader("배송 상세 정보"),
                    dbc.ModalBody(id="modal-body"),
                    dbc.ModalFooter(
                        dbc.Button("닫기", id="close-modal", className="ml-auto")
                    )
                ], id="detail-modal", size="lg"),
            ])
        ]),
        dbc.Tab(label="기사 현황", children=[
            html.Div([
                html.H1("실시간 기사 현황", className="text-center my-4"),

                # 기사 현황 통계
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H4("전체 기사 수", className="card-title"),
                            html.H2(id="total-drivers", className="card-text")
                        ])
                    ]), width=4),
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H4("현재 배송중", className="card-title"),
                            html.H2(id="active-drivers", className="card-text")
                        ])
                    ]), width=4),
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H4("금일 배송 완료율", className="card-title"),
                            html.H2(id="completion-rate", className="card-text")
                        ])
                    ]), width=4),
                ], className="mb-4"),

                # 기사 현황 테이블
                dbc.Table(id='driver-table', bordered=True, hover=True, responsive=True),
            ])
        ])
    ]),

    # 데이터 저장용 Store 컴포넌트
    dcc.Store(id='delivery-data'),
    dcc.Store(id='driver-data'),

    # 자동 갱신을 위한 인터벌 컴포넌트
    dcc.Interval(
        id='interval-component',
        interval=10000,  # 10초마다 갱신
        n_intervals=0
    )
], fluid=True)


# 데이터 갱신 콜백
@callback(
    [Output('delivery-data', 'data'),
     Output('driver-data', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('refresh-button', 'n_clicks')]
)
def update_data(_n, _clicks):
    delivery_df = generate_delivery_data()
    driver_df = generate_driver_status()
    return delivery_df.to_dict('records'), driver_df.to_dict('records')


# 배송 현황 테이블 업데이트 콜백
@callback(
    [Output('delivery-table', 'children'),
     Output('total-deliveries', 'children'),
     Output('in-progress', 'children'),
     Output('completed', 'children'),
     Output('sla-rate', 'children')],
    [Input('delivery-data', 'data')]
)
def update_delivery_table(data):
    if not data:
        return [], "0", "0", "0", "0%"

    df = pd.DataFrame(data)

    # 통계 계산
    total = len(df)
    in_progress = len(df[df['Status'] == 'shipping'])
    completed = len(df[df['Status'] == 'complete'])
    sla_rate = f"{(completed / total * 100):.1f}%" if total > 0 else "0%"

    # 테이블 헤더
    header = html.Thead(html.Tr([html.Th(col) for col in df.columns]))

    # 테이블 본문
    rows = []
    for idx, row in df.iterrows():
        # 상태에 따른 행 스타일 설정
        row_style = {}
        if row['Status'] == 'complete':
            row_style = {'backgroundColor': '#e8f5e9'}  # 연한 초록
        elif row['Status'] == 'shipping':
            row_style = {'backgroundColor': '#fff3e0'}  # 연한 주황

        rows.append(html.Tr([
            html.Td(row[col]) for col in df.columns
        ], id=f'row-{idx}', style=row_style, className='clickable-row'))

    body = html.Tbody(rows)

    return [header, body], str(total), str(in_progress), str(completed), sla_rate


# 기사 현황 테이블 업데이트 콜백
@callback(
    [Output('driver-table', 'children'),
     Output('total-drivers', 'children'),
     Output('active-drivers', 'children'),
     Output('completion-rate', 'children')],
    [Input('driver-data', 'data')]
)
def update_driver_table(data):
    if not data:
        return [], "0", "0", "0%"

    df = pd.DataFrame(data)

    # 통계 계산
    total_drivers = len(df)
    active_drivers = len(df[df['현재상태'] == '배송중'])
    completion_rate = f"{(df['완료건수'].sum() / df['오늘배송건수'].sum() * 100):.1f}%"

    # 테이블 헤더
    header = html.Thead(html.Tr([html.Th(col) for col in df.columns]))

    # 테이블 본문
    rows = []
    for idx, row in df.iterrows():
        # 상태에 따른 행 스타일 설정
        row_style = {}
        if row['현재상태'] == '배송완료':
            row_style = {'backgroundColor': '#e8f5e9'}
        elif row['현재상태'] == '배송중':
            row_style = {'backgroundColor': '#fff3e0'}
        elif row['현재상태'] == '복귀중':
            row_style = {'backgroundColor': '#f3e5f5'}

        rows.append(html.Tr([
            html.Td(row[col]) for col in df.columns
        ], style=row_style))

    body = html.Tbody(rows)

    return [header, body], str(total_drivers), str(active_drivers), completion_rate


# 배송 상세 정보 모달 콜백
@callback(
    [Output("detail-modal", "is_open"),
     Output("modal-body", "children")],
    [Input({'type': 'row', 'index': dash.ALL}, 'n_clicks')],
    [State('delivery-data', 'data')],
    prevent_initial_call=True
)
def show_delivery_details(n_clicks, data):
    if not dash.callback_context.triggered:
        return False, None

    triggered_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    row_idx = int(triggered_id.split('-')[1])

    if row_idx >= len(data):
        return False, None

    row_data = data[row_idx]

    detail_content = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H5("배송 상세 정보"),
                html.Hr(),
                html.P(f"DPS 번호: {row_data['DPS']}"),
                html.P(f"배송 기사: {row_data['Delivery']}"),
                html.P(f"수령인: {row_data['Recipient']}"),
                html.P(f"주소: {row_data['Address']}"),
                html.P(f"우편번호: {row_data['ZipCode']}"),
                html.P(f"상태: {row_data['Status']}"),
                html.P(f"출발 시간: {row_data['DepartTime']}"),
                html.P(f"도착 예정: {row_data['ETA']}"),
                html.P(f"SLA: {row_data['SLA']}")
            ])
        ])
    ])

    return True, detail_content


# CSS 스타일
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>실시간 배송 현황 대시보드</title>
        {%favicon%}
        {%css%}
        <style>
            .clickable-row {
                cursor: pointer;
            }
            .clickable-row:hover {
                background-color: #f5f5f5;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True)