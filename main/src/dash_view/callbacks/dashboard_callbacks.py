from dash import callback, Output, Input, State, no_update, ctx, html
from datetime import datetime
import dash_bootstrap_components as dbc

from ...services.dashboard_service import DashboardService
from ...schemas.delivery_schema import StatusUpdate, DriverAssignment

# 상태 매핑 (UI 표시용)
STATUS_MAP = {
    "WAITING": "대기",
    "IN_PROGRESS": "진행",
    "COMPLETED": "완료",
    "ISSUE": "이슈"
}

# UI 상태값을 API 값으로 변환
STATUS_REVERSE_MAP = {v: k for k, v in STATUS_MAP.items()}


@callback(
    [Output('table-data', 'data'),
     Output('status-toast', 'is_open'),
     Output('status-toast', 'header'),
     Output('status-toast', 'children')],
    Input('refresh-btn', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    """새로고침 버튼 클릭 시 데이터 갱신"""
    if not n_clicks:
        return no_update, False, "", ""

    service = DashboardService()
    if service.refresh_dashboard_data():
        data = service.get_dashboard_data()

        # UI 표시용 상태 추가
        for row in data:
            row['status_display'] = STATUS_MAP[row['status']]
            row['type_display'] = "배송" if row['type'] == "DELIVERY" else "회수"

        return data, True, "새로고침 완료", "데이터가 최신화되었습니다."
    else:
        return no_update, True, "오류 발생", "데이터 갱신 중 문제가 발생했습니다."


@callback(
    Output('delivery-table', 'data'),
    [Input('department-filter', 'value'),
     Input('status-filter', 'value'),
     Input('driver-filter', 'value'),
     Input('search-input', 'value'),
     Input('table-data', 'data')]
)
def filter_and_sort_table_data(dept_filter, status_filter, driver_filter, search_value, data):
    """클라이언트 사이드 필터링"""
    if not data:
        return []

    filtered_data = data.copy()
    now = datetime.now()

    # 필터 적용
    if dept_filter and dept_filter != 'all':
        filtered_data = [row for row in filtered_data if row['department'] == dept_filter]

    if status_filter and status_filter != 'all':
        filtered_status = STATUS_REVERSE_MAP.get(status_filter)
        filtered_data = [row for row in filtered_data if row['status'] == filtered_status]

    if driver_filter and driver_filter != 'all':
        filtered_data = [row for row in filtered_data if row['driver'] == driver_filter]

    if search_value:
        filtered_data = [row for row in filtered_data
                         if search_value.lower() in str(row['dps']).lower()]

    # ETA 처리 및 정렬
    for row in filtered_data:
        try:
            eta = datetime.strptime(row['eta'], '%Y-%m-%d %H:%M')
            row['_eta_diff'] = float('inf') if row['status'] == "COMPLETED" \
                else (eta - now).total_seconds()
        except:
            row['_eta_diff'] = float('inf')

    # 완료된 건은 맨 뒤로
    completed = [row for row in filtered_data if row['status'] == "COMPLETED"]
    pending = [row for row in filtered_data if row['status'] != "COMPLETED"]
    pending.sort(key=lambda x: x.get('_eta_diff', float('inf')))
    filtered_data = pending + completed

    # 임시 필드 제거
    for row in filtered_data:
        if '_eta_diff' in row:
            del row['_eta_diff']

    return filtered_data


@callback(
    [Output('delivery-table', 'style_data_conditional'),
     Output('error-toast', 'is_open'),
     Output('error-toast', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('delivery-table', 'data')]
)
def update_table_styles(n_intervals, data):
    """테이블 스타일 업데이트"""
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
                    'filter_query': '{status_display} = "대기"',
                    'column_id': 'status_display'
                },
                'color': '#854d0e',
                'fontWeight': 'bold'
            },
            {
                'if': {
                    'filter_query': '{status_display} = "진행"',
                    'column_id': 'status_display'
                },
                'color': '#1e40af',
                'fontWeight': 'bold'
            },
            {
                'if': {
                    'filter_query': '{status_display} = "완료"',
                    'column_id': 'status_display'
                },
                'color': '#166534',
                'fontWeight': 'bold'
            },
            {
                'if': {
                    'filter_query': '{status_display} = "이슈"',
                    'column_id': 'status_display'
                },
                'color': '#991b1b',
                'fontWeight': 'bold'
            }
        ]

        # ETA 기반 행 스타일
        for i, row in enumerate(data):
            if row['status'] != "COMPLETED":
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


@callback([Output("status-toast", "is_open", allow_duplicate=True),
           Output("delivery-table", "data", allow_duplicate=True),
           Output("detail-modal", "is_open", allow_duplicate=True)],
          [Input("confirm-status-change", "n_clicks")],
          [State("status-select", "value"),
           State("delivery-table", "active_cell"),
           State("delivery-table", "data")],
          prevent_initial_call=True
          )
def update_status(n_clicks, new_status, active_cell, data):
    """배송 상태 업데이트"""
    if not n_clicks or active_cell is None:
        return no_update, no_update, no_update

    service = DashboardService()
    delivery_id = data[active_cell['row']]['id']

    # 입력 데이터 검증
    status_update = StatusUpdate(
        delivery_id=delivery_id,
        new_status=STATUS_REVERSE_MAP[new_status]  # UI 상태값을 API 상태값으로 변환
    )

    if service.update_delivery_status(status_update):
        # 갱신된 데이터 조회
        updated_data = service.get_dashboard_data()
        # UI 표시용 상태 추가
        for row in updated_data:
            row['status_display'] = STATUS_MAP[row['status']]
            row['type_display'] = "배송" if row['type'] == "DELIVERY" else "회수"
        return True, updated_data, False

    return True, no_update, False


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
    """기사 할당 모달 핸들링"""
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
    """기사 할당 처리"""
    if not n_clicks or not driver or not selected_rows:
        return no_update

    service = DashboardService()

    # 입력 데이터 검증
    assignment = DriverAssignment(
        delivery_ids=[data[idx]['id'] for idx in selected_rows],
        driver_id=driver
    )

    if service.assign_driver(assignment):
        # 갱신된 데이터 조회
        updated_data = service.get_dashboard_data()
        # UI 표시용 상태 추가
        for row in updated_data:
            row['status_display'] = STATUS_MAP[row['status']]
            row['type_display'] = "배송" if row['type'] == "DELIVERY" else "회수"
        return updated_data

    return no_update


@callback(
    Output("assign-btn", "disabled"),
    [Input("delivery-table", "selected_rows")]
)
def toggle_assign_button(selected_rows):
    """할당 버튼 활성화/비활성화"""
    return not selected_rows
