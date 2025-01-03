# dashboard_callbacks.py
from dash import callback, Output, Input, State, no_update
import requests
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://127.0.0.1:5000/api/dashboard"

# 상태 매핑 (UI 표시용)
STATUS_MAP = {
    "WAITING": "대기",
    "IN_PROGRESS": "진행",
    "COMPLETED": "완료",
    "ISSUE": "이슈"
}


# 디버깅을 위한 콜백 추가
@callback(
    Output("debug-output", "children"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def debug_button_click(n_clicks):
    logger.info(f"디버그 콜백 호출됨: n_clicks = {n_clicks}")
    return f"버튼 클릭 횟수: {n_clicks}"


@callback(
    [Output('table-data', 'data'),
     Output('status-toast', 'is_open'),
     Output('status-toast', 'header'),
     Output('status-toast', 'children')],
    Input('refresh-btn', 'n_clicks'),
    prevent_initial_call=True
)
def fetch_delivery_data(n_clicks):
    """데이터 새로고침"""
    logger.info(f"fetch_delivery_data 콜백 실행: n_clicks = {n_clicks}")

    if n_clicks is None:
        logger.info("n_clicks가 None입니다.")
        return no_update, no_update, no_update, no_update

    try:
        logger.info("API 호출 시도")
        response = requests.get(f"{API_BASE_URL}/sync")
        logger.info(f"API 응답 상태 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json().get('data', [])
            logger.info(f"데이터 수신 성공: {len(data)} 건")
            return data, True, "성공", "데이터가 성공적으로 새로고침되었습니다."

        logger.error(f"API 호출 실패: {response.status_code}")
        return no_update, True, "오류", f"데이터 새로고침 실패: {response.status_code}"

    except Exception as e:
        logger.error(f"예외 발생: {str(e)}")
        return no_update, True, "오류", f"데이터 새로고침 중 오류 발생: {str(e)}"


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

    try:
        delivery_ids = [table_data[i]['dps'] for i in selected_rows]
        response = requests.post(
            f"{API_BASE_URL}/driver/assign",
            json={'delivery_ids': delivery_ids, 'driver_id': driver_id}
        )
        if response.status_code == 200:
            return True
        logger.error(f"Driver assignment failed: {response.text}")
        return no_update
    except Exception as e:
        logger.error(f"Error in driver assignment: {str(e)}")
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

    try:
        row = table_data[active_cell['row']]
        response = requests.put(
            f"{API_BASE_URL}/status",
            json={'delivery_id': row['dps'], 'new_status': new_status}
        )
        if response.status_code == 200:
            row['status'] = new_status
            return table_data
        logger.error(f"Status update failed: {response.text}")
        return no_update
    except Exception as e:
        logger.error(f"Error in status update: {str(e)}")
        return no_update


@callback(
    [Output('driver-filter', 'options'),
     Output('assign-driver-select', 'options')],
    Input('refresh-btn', 'n_clicks'),
    prevent_initial_call=True
)
def fetch_driver_list(n_clicks):
    """기사 목록 가져오기"""
    try:
        response = requests.get(f"{API_BASE_URL}/drivers")
        if response.status_code == 200:
            drivers = response.json().get('drivers', [])
            options = [{"label": driver['name'], "value": driver['id']} for driver in drivers]
            return options, options
        logger.error(f"Failed to fetch driver list: {response.text}")
        return no_update, no_update
    except Exception as e:
        logger.error(f"Error fetching driver list: {str(e)}")
        return no_update, no_update
