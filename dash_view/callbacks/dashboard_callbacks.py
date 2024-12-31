#dashboard_callbacks.py
from dash import callback, Output, Input, State, no_update, ctx, html
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
from ..mock_data import generate_sample_data


def format_status(status):
    """상태 코드를 텍스트로 변환"""
    status_map = {
        0: "대기",
        1: "진행",
        2: "완료",
        3: "이슈"
    }
    return status_map.get(status, status_map[0])


@callback(
    [Output('table-data', 'data'),
     Output('status-toast', 'is_open'),
     Output('status-toast', 'header'),
     Output('status-toast', 'children')],
    Input('refresh-btn', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    if n_clicks:
        try:
            new_data = generate_sample_data(100)
            return new_data, True, "새로고침 완료", "데이터가 최신화되었습니다."
        except Exception as e:
            return no_update, True, "오류 발생", "데이터 새로고침 중 문제가 발생했습니다."
    return no_update, False, "", ""


@callback(
    Output('delivery-table', 'data'),
    [Input('department-filter', 'value'),
     Input('status-filter', 'value'),
     Input('driver-filter', 'value'),
     Input('search-input', 'value'),
     Input('table-data', 'data')]
)
def filter_and_sort_table_data(dept_filter, status_filter, driver_filter, search_value, data):
    if not data:
        return []

    filtered_data = data.copy()
    now = datetime.now()

    # 필터 적용
    if dept_filter and dept_filter != 'all':
        filtered_data = [row for row in filtered_data if row['department'] == dept_filter]

    if status_filter and status_filter != 'all':
        filtered_data = [row for row in filtered_data if str(row['status']) == status_filter]

    if driver_filter and driver_filter != 'all':
        filtered_data = [row for row in filtered_data if row['driver'] == driver_filter]

    if search_value:
        filtered_data = [row for row in filtered_data if search_value.lower() in str(row['dps']).lower()]

    # 상태 변환 및 ETA 처리
    for row in filtered_data:
        # 타입을 텍스트로 변환
        row['type'] = "배송" if row['type'] == 0 else "회수"

        # 상태 처리
        if isinstance(row['status'], int):
            row['status'] = format_status(row['status'])

        # ETA 처리를 위한 임시 값
        try:
            eta = datetime.strptime(row['eta'], '%Y-%m-%d %H:%M')
            row['_eta_diff'] = float('inf') if row['status'] == "완료" else (eta - now).total_seconds()
        except:
            row['_eta_diff'] = float('inf')

    # ETA 기준 정렬 (완료는 맨 뒤로)
    completed = [row for row in filtered_data if row['status'] == "완료"]
    pending = [row for row in filtered_data if row['status'] != "완료"]
    pending.sort(key=lambda x: x.get('_eta_diff', float('inf')))
    filtered_data = pending + completed

    # 임시 필드 제거
    for row in filtered_data:
        if '_eta_diff' in row:
            del row['_eta_diff']

    return filtered_data


@callback(
    [Output('table-pagination', 'max_value'),
     Output('pagination-info', 'children')],
    [Input('delivery-table', 'data'),
     Input('delivery-table', 'page_current')]
)
def update_pagination(data, current_page):
    if not data:
        return 1, ""

    page_size = 15
    total = len(data)
    current_page = current_page or 0
    start = (current_page) * page_size + 1
    end = min((current_page + 1) * page_size, total)
    total_pages = (total + page_size - 1) // page_size

    return total_pages, f"{start:,}-{end:,} / 총 {total:,}건"


@callback(
    [Output('delivery-table', 'style_data_conditional'),
     Output('error-toast', 'is_open'),
     Output('error-toast', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('delivery-table', 'data')]
)
def update_table_styles(n_intervals, data):
    if not data:
        return no_update, False, no_update

    try:
        now = datetime.now()
        style_conditions = [
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#fafafa'
            },
            {
                'if': {'state': 'selected'},
                'backgroundColor': '#f1f8ff',
                'border': '1px solid #0ea5e9'
            },
            # 상태별 셀 스타일
            {
                'if': {
                    'filter_query': '{status} = "대기"',
                    'column_id': 'status'
                },
                'color': '#854d0e',
                'fontWeight': 'bold'
            },
            {
                'if': {
                    'filter_query': '{status} = "진행"',
                    'column_id': 'status'
                },
                'color': '#1e40af',
                'fontWeight': 'bold'
            },
            {
                'if': {
                    'filter_query': '{status} = "완료"',
                    'column_id': 'status'
                },
                'color': '#166534',
                'fontWeight': 'bold'
            },
            {
                'if': {
                    'filter_query': '{status} = "이슈"',
                    'column_id': 'status'
                },
                'color': '#991b1b',
                'fontWeight': 'bold'
            }
        ]

        # ETA 기반 행 스타일
        for i, row in enumerate(data):
            if row['status'] != "완료":
                try:
                    eta = datetime.strptime(row['eta'], '%Y-%m-%d %H:%M')
                    time_diff = (eta - now).total_seconds() / 60

                    if time_diff < 0:  # ETA 초과
                        style_conditions.append({
                            'if': {'row_index': i},
                            'backgroundColor': '#fee2e2'  # 빨간색 배경
                        })
                    elif time_diff < 30:  # ETA 임박
                        style_conditions.append({
                            'if': {'row_index': i},
                            'backgroundColor': '#fef9c3'  # 노란색 배경
                        })
                except:
                    continue

        return style_conditions, False, no_update

    except Exception as e:
        return no_update, True, "스타일 업데이트 중 오류가 발생했습니다."


@callback(
    [Output("detail-modal", "is_open"),
     Output("modal-content", "children"),
     Output("status-select", "value")],
    [Input("delivery-table", "active_cell"),
     Input("close-detail-modal", "n_clicks")],
    [State("delivery-table", "data"),
     State("detail-modal", "is_open")]
)
def toggle_detail_modal(active_cell, close_clicks, data, is_open):
    if close_clicks and ctx.triggered_id == "close-detail-modal":
        return False, no_update, no_update

    if active_cell is not None:
        row = data[active_cell['row']]
        content = html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label("DPS", className="text-muted mb-1"),
                    html.Div(row['dps'], className="border-bottom pb-2 mb-3"),
                ], width=6),
                dbc.Col([
                    dbc.Label("배송기사", className="text-muted mb-1"),
                    html.Div(row['driver'] or '-', className="border-bottom pb-2 mb-3"),
                ], width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("부서", className="text-muted mb-1"),
                    html.Div(row['department'], className="border-bottom pb-2 mb-3"),
                ], width=4),
                dbc.Col([
                    dbc.Label("작업타입", className="text-muted mb-1"),
                    html.Div(row['type'], className="border-bottom pb-2 mb-3"),
                ], width=4),
                dbc.Col([
                    dbc.Label("SLA", className="text-muted mb-1"),
                    html.Div(row['sla'], className="border-bottom pb-2 mb-3"),
                ], width=4),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("ETA", className="text-muted mb-1"),
                    html.Div(row['eta'], className="border-bottom pb-2 mb-3"),
                ], width=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("주소", className="text-muted mb-1"),
                    html.Div(row['address'], className="border-bottom pb-2 mb-3"),
                ], width=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("수령인", className="text-muted mb-1"),
                    html.Div(row['recipient'], className="border-bottom pb-2 mb-3"),
                ], width=12),
            ]),
        ])

        status_value = row['status']
        if isinstance(status_value, str):
            status_map = {"대기": "0", "진행": "1", "완료": "2", "이슈": "3"}
            status_value = status_map.get(status_value, "0")

        return True, content, status_value

    return no_update, no_update, no_update


@callback(
    [Output("status-toast", "is_open", allow_duplicate=True),
     Output("delivery-table", "data", allow_duplicate=True),
     Output("detail-modal", "is_open", allow_duplicate=True)],
    [Input("confirm-status-change", "n_clicks")],
    [State("status-select", "value"),
     State("delivery-table", "active_cell"),
     State("delivery-table", "data")],
    prevent_initial_call=True
)
def update_status(n_clicks, new_status, active_cell, data):
    if not n_clicks or active_cell is None:
        return no_update, no_update, no_update

    data = data.copy()
    status_map = {"0": "대기", "1": "진행", "2": "완료", "3": "이슈"}
    data[active_cell['row']]['status'] = status_map[new_status]

    return True, data, False


@callback(
    [Output("assign-modal", "is_open"),
     Output("selected-count-alert", "children"),
     Output("selected-orders-list", "children")],
    [Input("assign-btn", "n_clicks"),
     Input("close-assign-modal", "n_clicks"),
     Input("confirm-assign", "n_clicks")],
    [State("delivery-table", "selected_rows"),
     State("delivery-table", "data")]
)
def handle_assign_modal(n_open, n_close, n_confirm, selected_rows, data):
    if n_close or n_confirm or not selected_rows:
        return False, "", None

    if n_open:
        return True, f"선택된 배송: {len(selected_rows)}건", html.Div([
            html.H6("선택된 배송 목록:", className="mb-3"),
            html.Div([
                html.Div([
                    html.Strong(f"DPS: {data[idx]['dps']}", className="me-2"),
                    html.Span(data[idx]['address'])
                ], className="mb-2 p-2 border rounded")
                for idx in selected_rows
            ])
        ])

    return no_update, no_update, no_update


@callback(
    Output("delivery-table", "data", allow_duplicate=True),
    [Input("confirm-assign", "n_clicks")],
    [State("driver-select", "value"),
     State("delivery-table", "selected_rows"),
     State("delivery-table", "data")],
    prevent_initial_call=True
)
def assign_driver(n_clicks, driver, selected_rows, data):
    if not n_clicks or not driver or not selected_rows:
        return no_update

    data = data.copy()
    for idx in selected_rows:
        data[idx]['driver'] = driver
        if data[idx]['status'] == "대기":
            data[idx]['status'] = "진행"

    return data


@callback(
    Output("assign-btn", "disabled"),
    [Input("delivery-table", "selected_rows")]
)
def toggle_assign_button(selected_rows):
    return not selected_rows
