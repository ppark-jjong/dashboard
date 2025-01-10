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
            {'name': '연락처', 'id': 'contact'}
        ],
        data=[],
        page_action='custom',
        page_current=0,
        page_size=15,
        page_count=1,
        row_selectable='multi',
        selected_rows=[],

        # 기본 스타일 설정
        style_table={
            'width': '100%',
        },

        style_cell={
            'textAlign': 'left',
        },

        # 상태 컬럼 조건부 스타일
        style_data_conditional=[
            {
                'if': {'column_id': 'status', 'filter_query': '{status} eq "대기"'},
                'className': 'status-wait status-pill'
            },
            {
                'if': {'column_id': 'status', 'filter_query': '{status} eq "진행"'},
                'className': 'status-progress status-pill'
            },
            {
                'if': {'column_id': 'status', 'filter_query': '{status} eq "완료"'},
                'className': 'status-complete status-pill'
            },
            {
                'if': {'column_id': 'status', 'filter_query': '{status} eq "취소"'},
                'className': 'status-cancel status-pill'
            }
        ],

        css=[{
            'selector': '.dash-table-container',
            'rule': 'margin: 0; padding: 0;'
        }]
    )


def create_filter_controls():
    """필터링 컨트롤 생성"""
    return html.Div([
        dbc.Row([
            # 검색창
            dbc.Col(
                dbc.Input(
                    id="search-input",
                    placeholder="검색어를 입력하세요",
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
                        {"label": "완료", "value": "완료"}
                    ],
                    value="all",
                    className="form-select"
                ),
                width=2,
            ),
            dbc.Col(
                dbc.Select(
                    id="driver-filter",
                    options=[],
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
        ],
            className="g-3 align-items-center"
        ),
    ], className="filter-controls bg-white p-3 rounded shadow-sm mb-3")


def create_detail_modal():
    return dbc.Modal([
        dbc.ModalHeader("상세 정보", className="modal-header"),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([field_group("부서", "department")], width=6),
                dbc.Col([field_group("유형", "type")], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([field_group("창고", "warehouse")], width=6),
                dbc.Col([field_group("기사명", "driver_name")], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([field_group("DPS", "dps")], width=6),
                dbc.Col([field_group("SLA", "sla")], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("상태", className="modal-label"),
                    dbc.Select(
                        id="status-select",
                        options=[
                            {"label": "대기", "value": "대기"},
                            {"label": "진행", "value": "진행"},
                            {"label": "완료", "value": "완료"},
                            {"label": "취소", "value": "취소"}
                        ],
                        className="status-select"
                    ),
                    dbc.Button(
                        "상태 변경",
                        id="status-update-btn",
                        color="primary",
                        className="status-update-btn"
                    )
                ], width=6),
                dbc.Col([field_group("ETA", "eta")], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([field_group("주소", "address")], width=12),
            ], className="mb-3"),
            # 추가된 필드들
            dbc.Row([
                dbc.Col([field_group("고객명", "customer")], width=6),
                dbc.Col([field_group("연락처", "contact")], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([field_group("비고", "remark")], width=6),
                dbc.Col([field_group("출발 시간", "depart_time")], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([field_group("소요 시간", "duration_time")], width=12),
            ], className="mb-3"),
        ], className="modal-content-body"),
        dbc.ModalFooter(
            dbc.Button("닫기", id="close-modal", className="btn-close-modal")
        )
    ], id="detail-modal", size="lg")
def field_group(label, field_id):
    return html.Div([
        html.Label(label, className="field-label"),
        html.Div(id=f"modal-{field_id}", className="field-content")
    ], className="field-group")


def layout():
    """대시보드 레이아웃"""
    return html.Div([
        dcc.Store(id='table-data', data=[]),
        dcc.Store(id='detail-data', data={}),

        html.H1("배송/회수 대시보드", className="dashboard-title"),

        create_filter_controls(),

        dcc.Loading(
            id="loading-indicator",
            children=[
                html.Div([create_data_table()], className="table-container")
            ],
            type="circle",
        ),

        create_detail_modal(),

        dbc.Toast(
            id="status-update-toast",
            header="상태 업데이트",
            is_open=False,
            duration=3000,
            className="status-toast"
        )
    ], className="dashboard-layout")
