# src/dash_view/dashboard.py
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def create_filter_controls():
    """필터 컨트롤 생성"""
    return html.Div([
        # 디버그 출력을 위한 div 추가
        html.Div(id="debug-output", className="mb-2"),

        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.InputGroupText(html.I(className="fas fa-search")),
                    dbc.Input(
                        id="search-input",
                        placeholder="DPS 검색",
                        className="search-input"
                    ),
                ], size="lg", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("부서"),
                        dbc.Select(
                            id="department-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "CS", "value": "CS"},
                                {"label": "HES", "value": "HES"},
                                {"label": "Lenovo", "value": "Lenovo"}
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
                                {"label": "대기", "value": "WAITING"},
                                {"label": "진행", "value": "IN_PROGRESS"},
                                {"label": "완료", "value": "COMPLETED"},
                                {"label": "이슈", "value": "ISSUE"}
                            ],
                            value="all"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label("배송기사"),
                        dbc.Select(id="driver-filter", options=[], value="all")
                    ], width=4)
                ])
            ], width=8),
            dbc.Col([
                html.Div([
                    dbc.Button(
                        children=[
                            html.I(className="fas fa-sync-alt me-2"),
                            "새로고침"
                        ],
                        id="refresh-btn",
                        color="light",
                        className="me-2 shadow-sm",
                        n_clicks=0
                    ),
                    dbc.Button(
                        children=[
                            html.I(className="fas fa-user me-2"),
                            "기사 할당"
                        ],
                        id="assign-btn",
                        color="primary",
                        className="shadow-sm",
                        disabled=True,
                        n_clicks=0
                    ),
                ], className="d-flex justify-content-end align-items-end h-100")
            ], width=4),
        ]),
    ], className="mb-4 bg-white p-4 rounded shadow-sm")


def layout():
    """대시보드 레이아웃"""
    return html.Div([
        # 상태 저장소
        dcc.Store(id='table-data', data=[]),
        dcc.Store(id='filtered-indices', data=[]),
        dcc.Store(id='current-page', data=1),
        dcc.Interval(id='interval-component', interval=60 * 1000, n_intervals=0),

        # 메인 제목
        html.H1("배송 대시보드", className="dashboard-title mb-4"),

        # 필터 컨트롤
        create_filter_controls(),

        # 토스트 메시지
        dbc.Toast(
            id="status-toast",
            header="알림",
            is_open=False,
            dismissable=True,
            duration=3000,
            icon="success",
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),

        dbc.Toast(
            id="error-toast",
            header="오류",
            is_open=False,
            dismissable=True,
            duration=3000,
            icon="danger",
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),

        # 데이터 테이블
        html.Div([
            dash_table.DataTable(
                id='delivery-table',
                columns=[
                    {'name': '부서', 'id': 'department'},
                    {'name': '작업타입', 'id': 'type'},
                    {'name': '배송기사', 'id': 'driver'},
                    {'name': 'DPS', 'id': 'dps'},
                    {'name': 'SLA', 'id': 'sla'},
                    {'name': 'ETA', 'id': 'eta'},
                    {'name': '상태', 'id': 'status', 'presentation': 'markdown'},
                    {'name': '주소', 'id': 'address'},
                    {'name': '수령인', 'id': 'recipient'}
                ],
                data=[],
                style_table={
                    'overflowX': 'auto',
                    'borderRadius': '8px',
                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '16px',
                    'fontFamily': '"Pretendard", -apple-system, BlinkMacSystemFont, system-ui, sans-serif',
                    'fontSize': '14px',
                    'color': '#1f2937',
                    'border': 'none',
                    'maxWidth': '400px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis'
                },
                page_size=15,
                page_current=0,
                row_selectable='multi',
                selected_rows=[],
                page_action='native',
                sort_action='native',
                sort_mode='multi',
            )
        ], className="bg-white rounded shadow-sm p-4"),

        # 상세 정보 모달
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("배송 상세 정보")),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("현재 상태"),
                        dbc.Select(
                            id="status-select",
                            options=[
                                {"label": "대기", "value": "WAITING"},
                                {"label": "진행", "value": "IN_PROGRESS"},
                                {"label": "완료", "value": "COMPLETED"},
                                {"label": "이슈", "value": "ISSUE"}
                            ],
                            value="WAITING"
                        ),
                    ], width=6)
                ], className="mb-4"),
                html.Div(id="modal-content")
            ]),
            dbc.ModalFooter([
                dbc.Button("확인", id="confirm-status-change", color="primary", className="me-2"),
                dbc.Button("닫기", id="close-detail-modal")
            ])
        ], id="detail-modal", size="lg"),

        # 기사 할당 모달
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("기사 할당")),
            dbc.ModalBody([
                dbc.Alert(id="selected-count-alert", color="info", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("배정할 기사"),
                        dbc.Select(
                            id="assign-driver-select",
                            options=[]
                        )
                    ])
                ]),
                html.Div(id="selected-orders-list", className="mt-3")
            ]),
            dbc.ModalFooter([
                dbc.Button("할당", id="confirm-assign", color="primary", className="me-2"),
                dbc.Button("닫기", id="close-assign-modal")
            ])
        ], id="assign-modal", size="lg"),
    ])