from dash import html, dcc, register_page, callback, Output, Input, State, no_update, ctx, dash_table
import dash_bootstrap_components as dbc
from .callbacks.dashboard_callbacks import *
from .mock_data import generate_sample_data

register_page(__name__, path='/dashboard')

def create_filter_controls():
    return html.Div([
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
                                {"label": "대기", "value": "0"},
                                {"label": "진행", "value": "1"},
                                {"label": "완료", "value": "2"},
                                {"label": "이슈", "value": "3"}
                            ],
                            value="all"
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label("배송기사"),
                        dbc.Select(
                            id="driver-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "김운송", "value": "김운송"},
                                {"label": "이배달", "value": "이배달"},
                                {"label": "박퀵서비스", "value": "박퀵서비스"},
                                {"label": "최배송", "value": "최배송"},
                                {"label": "정기사", "value": "정기사"}
                            ],
                            value="all"
                        )
                    ], width=4)
                ])
            ], width=8),
            dbc.Col([
                html.Div([
                    dbc.Button(
                        [html.I(className="fas fa-sync-alt me-2"), "새로고침"],
                        id="refresh-btn",
                        color="light",
                        className="me-2 shadow-sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-user me-2"), "기사 할당"],
                        id="assign-btn",
                        color="primary",
                        className="shadow-sm",
                        disabled=True
                    ),
                ], className="d-flex justify-content-end align-items-end h-100")
            ], width=4),
        ]),
    ], className="mb-4 bg-white p-4 rounded shadow-sm")


def layout():
    data = generate_sample_data(100)

    return html.Div([
        dcc.Store(id='table-data', data=data),
        dcc.Store(id='filtered-indices', data=[]),
        dcc.Store(id='current-page', data=1),
        dcc.Interval(id='interval-component', interval=60 * 1000, n_intervals=0),

        html.H1("배송 대시보드", className="dashboard-title mb-4"),
        create_filter_controls(),

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
                data=data,
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
                style_header={
                    'backgroundColor': '#f8fafc',
                    'fontWeight': '600',
                    'padding': '16px',
                    'color': '#475569',
                    'border': 'none',
                    'borderBottom': '2px solid #e2e8f0'
                },
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8fafc',
                    },
                    {
                        'if': {'state': 'selected'},
                        'backgroundColor': '#e8f2ff',
                        'border': '1px solid #2563eb',
                    }
                ],
                css=[{
                    'selector': '.dash-table-pagination',
                    'rule': '''
                        padding: 16px;
                        background-color: #f8fafc;
                        border-top: 1px solid #e2e8f0;
                    '''
                }, {
                    'selector': '.dash-table-pagination .previous-next-container button',
                    'rule': '''
                        margin: 0 4px;
                        padding: 4px 8px;
                        border: 1px solid #e2e8f0;
                        border-radius: 4px;
                        background-color: white;
                        color: #1f2937;
                    '''
                }, {
                    'selector': '.dash-table-pagination .previous-next-container button:hover',
                    'rule': '''
                        background-color: #f1f5f9;
                        color: #2563eb;
                    '''
                }],
                page_size=15,
                page_current=0,
                row_selectable='multi',
                selected_rows=[],
                page_action='native',
                sort_action='native',
                sort_mode='multi',
            )
        ], className="bg-white rounded shadow-sm p-4"),

        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("배송 상세 정보")),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("현재 상태"),
                        dbc.Select(
                            id="status-select",
                            options=[
                                {"label": "대기", "value": "0"},
                                {"label": "진행", "value": "1"},
                                {"label": "완료", "value": "2"},
                                {"label": "이슈", "value": "3"}
                            ],
                            value="0"
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

        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("기사 할당")),
            dbc.ModalBody([
                dbc.Alert(id="selected-count-alert", color="info", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("배정할 기사"),
                        dbc.Select(
                            id="driver-select",
                            options=[
                                {"label": "김운송", "value": "김운송"},
                                {"label": "이배달", "value": "이배달"},
                                {"label": "박퀵서비스", "value": "박퀵서비스"},
                                {"label": "최배송", "value": "최배송"},
                                {"label": "정기사", "value": "정기사"}
                            ]
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