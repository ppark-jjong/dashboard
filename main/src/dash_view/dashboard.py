# src/dash_view/dashboard.py
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def create_data_table():
    """기본 데이터 테이블 생성"""
    return dash_table.DataTable(
        id='dashboard-table',
        columns=[
            {'name': '부서', 'id': 'department'},
            {'name': '유형', 'id': 'type'},  # delivery/return 구분
            {'name': '창고', 'id': 'warehouse'},
            {'name': '기사명', 'id': 'driver_name'},
            {'name': 'DPS', 'id': 'dps'},
            {'name': 'SLA', 'id': 'sla'},
            {'name': 'ETA', 'id': 'eta'},
            {'name': '상태', 'id': 'status', 'presentation': 'markdown'},
            {'name': '구역', 'id': 'district'},
            {'name': '연락처', 'id': 'contact'}
        ],
        data=[],
        style_table={
            'overflowX': 'auto',
            'borderRadius': '8px',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontFamily': '"Pretendard", sans-serif',
            'fontSize': '14px',
            'color': '#1f2937'
        },
        page_size=15,
        page_current=0,
        row_selectable='multi',
        selected_rows=[],
        page_action='native',
        sort_action='native',
        sort_mode='multi',
    )


def create_filter_controls():
    """필터링 컨트롤 생성"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.InputGroupText(html.I(className="fas fa-search")),
                    dbc.Input(id="search-input", placeholder="DPS 검색"),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("부서"),
                        dbc.Select(
                            id="department-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "CS", "value": "CS"},
                                {"label": "HES", "value": "HES"}
                            ],
                            value="all"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label("상태"),
                        dbc.Select(
                            id="status-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "대기", "value": "대기"},
                                {"label": "진행", "value": "진행"},
                                {"label": "완료", "value": "완료"}
                            ],
                            value="all"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label("기사"),
                        dbc.Select(id="driver-filter", options=[], value="all")
                    ], width=4)
                ])
            ], width=8),
            dbc.Col([
                html.Div([
                    dbc.Button(
                        [html.I(className="fas fa-sync-alt me-2"), "새로고침"],
                        id="refresh-btn",
                        color="light",
                        className="me-2",
                        n_clicks=0
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-user me-2"), "기사 할당"],
                        id="assign-btn",
                        color="primary",
                        disabled=True,
                        n_clicks=0
                    ),
                ], className="d-flex justify-content-end align-items-end h-100")
            ], width=4),
        ]),
    ], className="mb-4 bg-white p-4 rounded shadow-sm")


def create_detail_modal():
    """상세정보 모달 생성"""
    return dbc.Modal([
        dbc.ModalHeader("상세 정보"),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([field_group("부서", "department")], width=6),
                dbc.Col([field_group("유형", "type")], width=6),
            ]),
            dbc.Row([
                dbc.Col([field_group("창고", "warehouse")], width=6),
                dbc.Col([field_group("기사명", "driver_name")], width=6),
            ]),
            dbc.Row([
                dbc.Col([field_group("DPS", "dps")], width=6),
                dbc.Col([field_group("SLA", "sla")], width=6),
            ]),
            dbc.Row([
                dbc.Col([field_group("상태", "status")], width=6),
                dbc.Col([field_group("ETA", "eta")], width=6),
            ]),
            dbc.Row([
                dbc.Col([field_group("주소", "address")], width=12),
            ]),
            dbc.Row([
                dbc.Col([field_group("고객명", "customer")], width=6),
                dbc.Col([field_group("연락처", "contact")], width=6),
            ]),
            dbc.Row([
                dbc.Col([field_group("비고", "remark")], width=12),
            ]),
            dbc.Row([
                dbc.Col([field_group("출발시간", "depart_time")], width=6),
                dbc.Col([field_group("소요시간", "duration_time")], width=6),
            ]),
        ]),
        dbc.ModalFooter(
            dbc.Button("닫기", id="close-modal", className="ms-auto")
        )
    ], id="detail-modal", size="lg")


def field_group(label, field_id):
    """상세정보 필드 그룹 생성"""
    return html.Div([
        html.Label(label, className="fw-bold"),
        html.Div(id=f"detail-{field_id}", className="mt-1")
    ], className="mb-3")


def layout():
    """대시보드 레이아웃 구성"""
    return html.Div([
        # 데이터 저장소
        dcc.Store(id='table-data', data=[]),
        dcc.Store(id='detail-data', data={}),
        dcc.Interval(id='refresh-interval', interval=60 * 1000, n_intervals=0),

        # 메인 컨텐츠
        html.H1("배송/회수 대시보드", className="mb-4"),
        create_filter_controls(),
        html.Div([create_data_table()], className="bg-white rounded shadow-sm p-4"),
        create_detail_modal(),

        # 알림 토스트
        dbc.Toast(
            id="notification-toast",
            header="알림",
            is_open=False,
            duration=3000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        )
    ])