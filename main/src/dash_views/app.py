import dash
from dash import html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
from data.sample_data import generate_sample_data
from datetime import datetime
import pytz
import os

# 정적 파일 경로 설정
ASSETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

# 외부 스타일시트 설정
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    'https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap'
]

# Dash 앱 초기화
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    assets_folder=ASSETS_PATH,
    assets_url_path='assets'
)

def sort_data(data):
    """ETA 기준 정렬 + 완료 상태 후순위 처리"""
    def get_sort_key(item):
        eta = datetime.strptime(item['eta'], '%Y-%m-%d %H:%M')
        is_complete = item['status'] == 2
        return (is_complete, eta)
    return sorted(data, key=get_sort_key)

INITIAL_DATA = sort_data(generate_sample_data())

# 상태 레이블 정의
STATUS_LABELS = {
    0: '대기',
    1: '진행',
    2: '완료',
    3: '이슈'
}

def create_info_section(label, value):
    """상세 정보 섹션 생성"""
    return html.Span([
        html.Span(f"{label}: ", style={'color': '#64748b', 'marginRight': '8px', 'fontWeight': '500'}),
        html.Span(str(value) if value is not None else '-', style={'marginRight': '24px', 'color': '#0f172a'})
    ])

# 앱 레이아웃
app.layout = html.Div([
    # 네비게이션 바
    html.Nav(className='navbar', children=[
        html.A('Delivery Dashboard', className='navbar-brand'),
        html.Span('v1.0', className='navbar-text text-dark ml-2')
    ]),

    # 메인 컨테이너
    html.Div(className='main-container', children=[
        # 콘텐츠 래퍼
        html.Div(className='content-wrapper', children=[
            # 컨트롤 섹션
            html.Div(className='control-section', children=[
                dcc.Input(
                    id='search-input',
                    type='text',
                    placeholder='DPS번호, 배송기사, 주소로 검색...',
                    className='search-input',
                    style={'flex': '1'}
                ),
                dbc.Button(
                    "기사 할당",
                    id="open-driver-modal",
                    className="driver-assign-btn",
                    disabled=True
                )
            ]),

            # 데이터 테이블
            html.Div(className='table-container', children=[
                dash_table.DataTable(
                    id='delivery-table',
                    columns=[
                        {'name': '부서', 'id': 'department'},
                        {'name': '작업타입', 'id': 'type', 'presentation': 'dropdown'},
                        {'name': '배송기사', 'id': 'driver'},
                        {'name': 'DPS번호', 'id': 'dps'},
                        {'name': 'SLA', 'id': 'sla'},
                        {'name': 'ETA', 'id': 'eta'},
                        {'name': '상태', 'id': 'status', 'presentation': 'dropdown'},
                        {'name': '주소', 'id': 'address'},
                        {'name': '수령인', 'id': 'recipient'}
                    ],
                    data=INITIAL_DATA,
                    page_size=15,
                    page_current=0,
                    page_action='native',
                    row_selectable='multi',
                    selected_rows=[],
                    style_cell_conditional=[
                        {'if': {'column_id': 'department'},
                         'width': '100px',
                         'textAlign': 'left'},
                        {'if': {'column_id': 'type'},
                         'width': '100px'},
                        {'if': {'column_id': 'driver'},
                         'width': '120px',
                         'textAlign': 'left'},
                        {'if': {'column_id': 'dps'},
                         'width': '140px',
                         'textAlign': 'left'},
                        {'if': {'column_id': 'sla'},
                         'width': '80px',
                         'textAlign': 'center'},
                        {'if': {'column_id': 'eta'},
                         'width': '130px',
                         'textAlign': 'center'},
                        {'if': {'column_id': 'status'},
                         'width': '100px',
                         'textAlign': 'center'},
                        {'if': {'column_id': 'address'},
                         'width': '250px',
                         'textAlign': 'left'},
                        {'if': {'column_id': 'recipient'},
                         'width': '180px',
                         'textAlign': 'left'}
                    ],
                    style_cell={
                        'padding': '12px 15px',
                        'fontFamily': 'Pretendard, sans-serif',
                        'fontSize': '14px',
                        'border': 'none'
                    },
                    style_header={
                        'backgroundColor': '#f8fafc',
                        'fontWeight': '600',
                        'textAlign': 'left',
                        'fontSize': '14px',
                        'color': '#475569',
                        'border': 'none',
                        'borderBottom': '2px solid #e2e8f0',
                        'padding': '16px 15px'
                    },
                    style_data={
                        'backgroundColor': 'white',
                        'color': '#334155',
                        'borderBottom': '1px solid #f1f5f9'
                    },
                    style_table={
                        'borderRadius': '12px',
                        'overflow': 'hidden',
                        'border': '1px solid #e2e8f0'
                    },
                    dropdown={
                        'type': {
                            'options': [
                                {'label': '배송', 'value': 0},
                                {'label': '회수', 'value': 1}
                            ]
                        },
                        'status': {
                            'options': [
                                {'label': label, 'value': status}
                                for status, label in STATUS_LABELS.items()
                            ]
                        }
                    }
                )
            ])
        ]),

        # 상세 정보 모달
        dbc.Modal([
            dbc.ModalHeader(html.H5("배송 상세 정보", className='modal-title')),
            dbc.ModalBody(id='detail-modal-body'),
            dbc.ModalFooter(
                dbc.Button("닫기", id="close-detail-modal", className="ml-auto")
            )
        ], id='detail-modal', className='custom-modal'),

        # 기사 할당 모달
        dbc.Modal([
            dbc.ModalHeader(html.H5("기사 할당", className='modal-title')),
            dbc.ModalBody([
                html.Div([
                    html.Label("배정할 기사 선택", className='mb-2'),
                    dcc.Dropdown(
                        id='driver-select',
                        options=[
                            {'label': '김운송', 'value': '김운송'},
                            {'label': '이배달', 'value': '이배달'},
                            {'label': '박퀵서비스', 'value': '박퀵서비스'},
                            {'label': '최배송', 'value': '최배송'},
                            {'label': '정기사', 'value': '정기사'}
                        ],
                        multi=True,
                        placeholder='기사를 선택하세요'
                    ),
                    html.Div(id='selected-orders', className='mt-3')
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("취소", id="close-driver-modal", color="secondary"),
                dbc.Button("할당", id="assign-driver", color="primary")
            ])
        ], id='driver-modal', className='custom-modal')
    ])
])

# 콜백: 검색 기능
@callback(
    Output('delivery-table', 'data'),
    Input('search-input', 'value')
)
def update_table(search_value):
    data = INITIAL_DATA.copy()
    if search_value:
        search_value = search_value.lower()
        data = [
            row for row in data
            if any(str(value).lower().find(search_value) != -1
                   for value in row.values())
        ]
    return data

# 콜백: 상세 정보 모달 표시
@callback(
    [Output('detail-modal', 'is_open'),
     Output('detail-modal-body', 'children')],
    Input('delivery-table', 'active_cell'),
    [State('delivery-table', 'data'),
     State('detail-modal', 'is_open')]
)
def show_detail_modal(active_cell, data, is_open):
    if active_cell is None:
        return is_open, None

    row = data[active_cell['row']]
    type_map = {0: '배송', 1: '회수'}

    content = html.Div(
        style={'padding': '20px'},
        children=[
            html.Div([
                create_info_section('DPS번호', row['dps']),
                create_info_section('상태', STATUS_LABELS[row['status']]),
                create_info_section('작업타입', type_map[row['type']]),
                create_info_section('부서', row['department']),
                create_info_section('배송기사', row['driver']),
                create_info_section('주소', row['address']),
                create_info_section('수령인', row['recipient']),
                create_info_section('ETA', row['eta']),
                create_info_section('SLA', row['sla']),
                create_info_section('출발시간', row.get('depart_time')),
                create_info_section('도착시간', row.get('arrive_time')),
                create_info_section('소요시간', f"{row.get('delivery_duration')}분"),
            ]),
            html.Div(
                style={'marginTop': '12px', 'display': 'block' if row.get('reason') else 'none'},
                children=[create_info_section('이슈사유', row.get('reason'))]
            )
        ]
    )

    return True, content

# 콜백: 상세 정보 모달 닫기
@callback(
    Output('detail-modal', 'is_open', allow_duplicate=True),
    Input('close-detail-modal', 'n_clicks'),
    prevent_initial_call=True
)
def close_detail_modal(n_clicks):
    return False

# 콜백: 기사 할당 버튼 활성화/비활성화
@callback(
    Output("open-driver-modal", "disabled"),
    Input("delivery-table", "selected_rows")
)
def toggle_assign_button(selected_rows):
    return not selected_rows

# 콜백: 기사 할당 모달 제어
@callback(
    [Output("driver-modal", "is_open"),
     Output("selected-orders", "children")],
    [Input("open-driver-modal", "n_clicks"),
     Input("close-driver-modal", "n_clicks"),
     Input("assign-driver", "n_clicks")],
    [State("delivery-table", "selected_rows"),
     State("delivery-table", "data"),
     State("driver-modal", "is_open")]
)
def toggle_driver_modal(n_open, n_close, n_assign, selected_rows, data, is_open):
    if not selected_rows:
        return False, None

    selected_data = [data[idx] for idx in selected_rows]
    orders_display = html.Div([
        html.H6(f"선택된 배송 건 ({len(selected_data)}건)", className='mb-3'),
        html.Div([
            html.Div(f"DPS: {row['dps']} - {row['address']}", className='selected-order-item')
            for row in selected_data
        ])
    ])

    if n_close or n_assign:
        return False, orders_display
    if n_open:
        return True, orders_display
    return is_open, orders_display

# 콜백: 기사 할당 처리
@callback(
    Output('delivery-table', 'data', allow_duplicate=True),
    [Input('assign-driver', 'n_clicks')],
    [State('driver-select', 'value'),
     State('delivery-table', 'selected_rows'),
     State('delivery-table', 'data')],
    prevent_initial_call=True
)
def assign_drivers(n_clicks, selected_drivers, selected_rows, data):
    if not n_clicks or not selected_drivers or not selected_rows:
        return data

    new_data = data.copy()
    for idx in selected_rows:
        new_data[idx]['driver'] = ', '.join(selected_drivers)
        if new_data[idx]['status'] == 0:
            new_data[idx]['status'] = 1

    return new_data

if __name__ == '__main__':
    app.run_server(debug=True)