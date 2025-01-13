# src/dash_view/dashboard.py
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def create_data_table():
    """데이터 테이블 생성"""
    return dash_table.DataTable(
        id='dashboard-table',
        columns=[
            {'name': '부서', 'id': 'department'},
            {'name': '유형', 'id': 'type'},
            {'name': '창고', 'id': 'warehouse'},
            {'name': '기사명', 'id': 'driver_name'},
            {'name': 'DPS', 'id': 'dps'},
            {'name': 'SLA', 'id': 'sla'},
            {'name': 'ETA', 'id': 'eta'},
            {
                'name': '상태',
                'id': 'status',
                'presentation': 'dropdown'
            },
            {'name': '도착지역', 'id': 'district'},
            {'name': '연락처', 'id': 'contact'},
            {'name': '소요시간', 'id': 'duration_time'}
        ],
        data=[],
        page_action='custom',
        page_current=0,
        page_size=15,
        page_count=1,
        row_selectable='multi',
        selected_rows=[],

        style_table={'width': '100%'},
        style_cell={'textAlign': 'left'},

        style_data_conditional=[
            {
                'if': {'column_id': 'status', 'filter_query': '{status} eq "대기"'},
                'backgroundColor': '#FFF3E0',
                'color': '#E65100'
            },
            {
                'if': {'column_id': 'status', 'filter_query': '{status} eq "진행"'},
                'backgroundColor': '#E3F2FD',
                'color': '#1565C0'
            },
            {
                'if': {'column_id': 'status', 'filter_query': '{status} eq "완료"'},
                'backgroundColor': '#E8F5E9',
                'color': '#2E7D32'
            },
            {
                'if': {'column_id': 'status', 'filter_query': '{status} eq "이슈"'},
                'backgroundColor': '#FFEBEE',
                'color': '#C62828'
            }
        ],
    )


def create_filter_controls():
    """필터링 컨트롤 생성"""
    return html.Div([
        dbc.Row([
            # 검색창
            dbc.Col(
                dbc.Input(
                    id="search-input",
                    placeholder="DPS 또는 고객명으로 검색",
                    className="form-control"
                ),
                width=3,
            ),

            # 필터 셀렉트 박스들
            dbc.Col(
                dbc.Select(
                    id="department-filter",
                    options=[
                        {"label": "전체 부서", "value": "all"},
                        {"label": "CS", "value": "CS"},
                        {"label": "HES", "value": "HES"}
                    ],
                    value="all",
                    className="form-select"
                ),
                width=2,
            ),
            dbc.Col(
                dbc.Select(
                    id="status-filter",
                    options=[
                        {"label": "전체 상태", "value": "all"},
                        {"label": "대기", "value": "대기"},
                        {"label": "진행", "value": "진행"},
                        {"label": "완료", "value": "완료"},
                        {"label": "이슈", "value": "이슈"}
                    ],
                    value="all",
                    className="form-select"
                ),
                width=2,
            ),
            dbc.Col(
                dbc.Select(
                    id="driver-filter",
                    options=[],  # 동적으로 로드됨
                    placeholder="기사 선택",
                    value="all",
                    className="form-select"
                ),
                width=2,
            ),

            # 버튼 그룹
            dbc.Col(
                html.Div([
                    dbc.Button(
                        [html.I(className="fas fa-sync-alt me-1"), "새로고침"],
                        id="refresh-btn",
                        color="light",
                        className="me-2"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-user me-1"), "기사 할당"],
                        id="assign-btn",
                        color="primary",
                        disabled=True
                    ),
                ], className="d-flex justify-content-end"),
                width=3,
            ),
        ], className="g-3 align-items-center"),
    ], className="filter-controls bg-white p-3 rounded shadow-sm mb-3")


def create_detail_modal():
    """상세 정보 모달"""
    return dbc.Modal([
        dbc.ModalHeader("상세 정보"),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    html.Strong("DPS: "),
                    html.Span(id="modal-dps"),
                ], width=6),
                dbc.Col([
                    html.Strong("상태: "),
                    dbc.Select(
                        id="status-select",
                        options=[
                            {"label": "대기", "value": "대기"},
                            {"label": "진행", "value": "진행"},
                            {"label": "완료", "value": "완료"},
                            {"label": "이슈", "value": "이슈"}
                        ],
                    ),
                    dbc.Button(
                        "상태 변경",
                        id="status-update-btn",
                        color="primary",
                        className="ms-2"
                    )
                ], width=6),
            ], className="mb-3"),
            # 기타 상세 정보 필드들...
        ]),
        dbc.ModalFooter(
            dbc.Button("닫기", id="close-modal", className="ms-auto")
        )
    ], id="detail-modal")


def layout():
    """대시보드 레이아웃"""
    return html.Div([
        dcc.Store(id='table-data'),

        html.H1("배송/회수 대시보드", className="mb-4"),

        create_filter_controls(),

        dcc.Loading(
            id="loading-table",
            children=[
                create_data_table()
            ],
            type="circle",
        ),

        create_detail_modal(),

        # 토스트 메시지
        dbc.Toast(
            id="notification-toast",
            header="알림",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),

    ], className="container-fluid py-4")