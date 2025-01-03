# dashboard_callbacks.py
from dash import callback, Output, Input, State, no_update
import requests

API_BASE_URL = "http://localhost:5000/"

# 상태 매핑 (UI 표시용)
STATUS_MAP = {
    "WAITING": "대기",
    "IN_PROGRESS": "진행",
    "COMPLETED": "완료",
    "ISSUE": "이슈"
}


@callback(
    Output('table-data', 'data'),
    Input('refresh-btn', 'n_clicks'),
    prevent_initial_call=True
)
def fetch_delivery_data(n_clicks):
    """Redis에서 배송 데이터 가져오기"""
    response = requests.get(f"{API_BASE_URL}/sync")
    if response.status_code == 200:
        return response.json().get('data', [])
    print("API 호출 실패:", response.status_code)
    return no_update


@callback(
    Output('delivery-table', 'data'),
    [Input('search-input', 'value'),
     Input('department-filter', 'value'),
     Input('status-filter', 'value')],
    State('table-data', 'data'),
    prevent_initial_call=True
)
def filter_table(search_value, department, status, table_data):
    """검색어 및 필터 조합에 따른 데이터 필터링"""
    filtered_data = table_data
    if search_value:
        filtered_data = [row for row in filtered_data if search_value.lower() in row['dps'].lower()]
    if department != 'all':
        filtered_data = [row for row in filtered_data if row['department'] == department]
    if status != 'all':
        filtered_data = [row for row in filtered_data if row['status'] == status]
    return filtered_data


@callback(
    Output('status-toast', 'is_open'),
    Input('confirm-assign', 'n_clicks'),
    State('delivery-table', 'selected_rows'),
    State('driver-select', 'value'),
    State('delivery-table', 'data'),
    prevent_initial_call=True
)
def assign_driver_to_deliveries(n_clicks, selected_rows, driver_id, table_data):
    """기사 할당 로직"""
    if not selected_rows or not driver_id:
        return no_update

    delivery_ids = [table_data[i]['dps'] for i in selected_rows]
    response = requests.post(
        f"{API_BASE_URL}/driver/assign",
        json={'delivery_ids': delivery_ids, 'driver_id': driver_id}
    )
    if response.status_code == 200:
        return True
    return no_update


@callback(
    Output('table-data', 'data'),
    Input('confirm-status-change', 'n_clicks'),
    State('status-select', 'value'),
    State('delivery-table', 'active_cell'),
    State('table-data', 'data'),
    prevent_initial_call=True
)
def update_delivery_status(n_clicks, new_status, active_cell, table_data):
    """배송 상태 업데이트 로직"""
    if not active_cell or not new_status:
        return no_update

    row = table_data[active_cell['row']]
    response = requests.put(
        f"{API_BASE_URL}/status",
        json={'delivery_id': row['dps'], 'new_status': new_status}
    )
    if response.status_code == 200:
        row['status'] = new_status
        return table_data
    return no_update


@callback(
    [Output('driver-filter', 'options'),  # 변경된 ID
     Output('assign-driver-select', 'options')],  # 변경된 ID
    Input('refresh-btn', 'n_clicks'),
    prevent_initial_call=True
)
def fetch_driver_list(n_clicks):
    """기사 목록 가져오기"""
    response = requests.get(f"{API_BASE_URL}/drivers")
    if response.status_code == 200:
        drivers = response.json().get('drivers', [])
        options = [{"label": driver['name'], "value": driver['id']} for driver in drivers]
        return options, options
    return no_update, no_update
