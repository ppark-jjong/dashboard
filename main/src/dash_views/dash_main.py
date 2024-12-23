import dash
from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import json
from datetime import datetime
import redis

# Redis 연결
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 상태 매핑
delivery_status_map = {0: '대기', 1: '배송', 2: '완료', 3: '이슈'}
return_status_list = ['대기', '회수중', '회수완료', '이슈']

# Dash 앱 초기화
dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# 페이지당 행 수
ROWS_PER_PAGE = 10


def get_data_from_redis():
    # Redis에서 모든 키 가져오기
    all_keys = redis_client.keys('delivery:*') + redis_client.keys('return:*')
    data = []

    for key in all_keys:
        item = redis_client.hgetall(key)
        if item:
            # bytes를 문자열로 디코딩
            item = {k.decode('utf-8'): v.decode('utf-8') for k, v in item.items()}
            data.append(item)

    return pd.DataFrame(data)


# 테이블 컴포넌트
def create_table(df, page=0):
    if df.empty:
        return html.Div("No model available")

    # 페이징 처리
    start_idx = page * ROWS_PER_PAGE
    end_idx = start_idx + ROWS_PER_PAGE
    page_data = df.iloc[start_idx:end_idx]

    return dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("부서", className="text-primary"),
                html.Th("타입", className="text-primary"),
                html.Th("DPS", className="text-primary"),
                html.Th("배송기사", className="text-primary"),
                html.Th("상태", className="text-primary"),
                html.Th("ETA", className="text-primary"),
                html.Th("주소", className="text-primary")
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(row['department']),
                html.Td(row['type']),
                html.Td(row['dps']),
                html.Td(row['delivery'] if pd.notna(row['delivery']) else '-'),
                html.Td(
                    delivery_status_map.get(int(row['status']), row['status'])
                    if row['type'] == 'delivery' else row['status'],
                    className=get_status_class(row['status'])
                ),
                html.Td(format_datetime(row['eta'])),
                html.Td(row['address'])
            ], id={'type': 'row', 'index': row['dps']},
                className='table-row-hover')
            for _, row in page_data.iterrows()
        ])
    ], bordered=True, hover=True, responsive=True, className='custom-table')


# 메인 레이아웃
dash_app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("배송/회수 현황 대시보드", className="dashboard-title my-4"),
            html.Div(id='table-container'),
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("이전", id="prev-page", color="primary", outline=True),
                        dbc.Button("다음", id="next-page", color="primary", outline=True),
                    ], className="me-2"),
                    html.Span(id="page-info", className="text-muted")
                ], width={"size": 6}),
                dbc.Col([
                    dbc.Input(
                        type="text",
                        placeholder="DPS 번호 검색...",
                        id="search-input",
                        className="mb-3"
                    )
                ], width={"size": 6})
            ], className="my-3"),

            # 상세 정보 모달
            dbc.Modal([
                dbc.ModalHeader("상세 정보"),
                dbc.ModalBody(id="modal-body"),
                dbc.ModalFooter(
                    dbc.Button("닫기", id="close-modal", className="ms-auto")
                )
            ], id="detail-modal", size="lg"),

            # 상태 변경 모달
            dbc.Modal([
                dbc.ModalHeader("상태 변경"),
                dbc.ModalBody([
                    dbc.Select(
                        id="status-select",
                        options=[],  # 동적으로 업데이트됨
                    ),
                    dbc.Input(
                        id="reason-input",
                        placeholder="사유 입력 (이슈 상태 선택 시)",
                        className="mt-3",
                        style={"display": "none"}
                    )
                ]),
                dbc.ModalFooter([
                    dbc.Button("취소", id="cancel-status", className="me-2"),
                    dbc.Button("저장", id="save-status", color="primary")
                ])
            ], id="status-modal"),

            # 컨텍스트 메뉴
            dbc.Popover(
                id="context-menu",
                target="table-container",
                trigger="legacy",
                style={"display": "none"}
            )
        ])
    ])
], fluid=True, className="dashboard-container")


# 콜백 함수들
@dash_app.callback(
    [Output('table-container', 'children'),
     Output('page-info', 'children')],
    [Input('prev-page', 'n_clicks'),
     Input('next-page', 'n_clicks'),
     Input('search-input', 'value')],
    [State('page-info', 'children')]
)
def update_table(prev_clicks, next_clicks, search_value, current_page_info):
    df = get_data_from_redis()

    if search_value:
        df = df[df['dps'].str.contains(search_value, case=False)]

    total_pages = (len(df) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE
    current_page = 0 if current_page_info is None else int(current_page_info.split('/')[0]) - 1

    if ctx.triggered_id == 'prev-page' and current_page > 0:
        current_page -= 1
    elif ctx.triggered_id == 'next-page' and current_page < total_pages - 1:
        current_page += 1

    table = create_table(df, current_page)
    page_info = f"{current_page + 1}/{total_pages}"

    return table, page_info


# 상세 정보 모달 콜백
@dash_app.callback(
    [Output("detail-modal", "is_open"),
     Output("modal-body", "children")],
    [Input({'type': 'row', 'index': dash.ALL}, 'n_clicks')],
    [State("detail-modal", "is_open")]
)
def toggle_modal(n_clicks, is_open):
    if not any(n_clicks) or not ctx.triggered_id:
        raise PreventUpdate

    dps = ctx.triggered_id['index']
    data = redis_client.hgetall(f"delivery:{dps}")

    if not data:
        data = redis_client.hgetall(f"return:{dps}")

    if data:
        data = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
        detail_content = dbc.Row([
            dbc.Col([
                html.H5("기본 정보"),
                html.Hr(),
                dbc.Row([
                    dbc.Col(html.Strong("DPS: "), width=4),
                    dbc.Col(data.get('dps', '-'), width=8)
                ], className="mb-2"),
                # ... 다른 상세 정보 필드들
            ])
        ])
        return True, detail_content

    return False, None


# 상태 변경 모달 콜백
@dash_app.callback(
    [Output("status-modal", "is_open"),
     Output("status-select", "options")],
    [Input("context-menu", "is_open")],
    [State("context-menu", "target_id")]
)
def show_status_modal(is_open, target_id):
    if not is_open or not target_id:
        raise PreventUpdate

    dps = target_id['index']
    data_type = redis_client.hget(f"delivery:{dps}", 'type')

    if data_type:
        data_type = data_type.decode('utf-8')
        options = [{"label": s, "value": s} for s in
                   (delivery_status_map.values() if data_type == 'delivery'
                    else return_status_list)]
        return True, options

    return False, []


# 유틸리티 함수들
def format_datetime(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_str


def get_status_class(status):
    status_classes = {
        '대기': 'text-warning',
        '배송': 'text-primary',
        '완료': 'text-success',
        '이슈': 'text-danger',
        '회수중': 'text-info',
        '회수완료': 'text-success'
    }
    return status_classes.get(str(status), '')


# CSS 스타일
dash_app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>배송/회수 현황 대시보드</title>
        {%favicon%}
        {%css%}
        <style>
            .dashboard-container {
                padding: 2rem;
                background-color: #f8f9fa;
            }
            .dashboard-title {
                color: #2c3e50;
                font-weight: 600;
            }
            .custom-table {
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .table-row-hover:hover {
                cursor: pointer;
                background-color: #f1f8ff !important;
            }
            .text-primary { color: #3498db !important; }
            .text-success { color: #2ecc71 !important; }
            .text-warning { color: #f1c40f !important; }
            .text-danger { color: #e74c3c !important; }
            .text-info { color: #3498db !important; }
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
    dash_app.run_server(debug=True)