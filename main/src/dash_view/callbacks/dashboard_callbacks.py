# src/dash_view/dashboard_callbacks.py
from dash import Input, Output, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
BASE_URL = 'http://localhost:5000/api/dashboard'


@callback(
    [Output('assign-modal', 'is_open'),
     Output('selected-count', 'children'),
     Output('driver-select', 'options')],
    [Input('assign-btn', 'n_clicks'),
     Input('close-assign-modal', 'n_clicks')],
    [State('dashboard-table', 'selected_rows'),
     State('dashboard-table', 'data')],
    prevent_initial_call=True
)
def toggle_assign_modal(assign_clicks, close_clicks, selected_rows, data):
    """기사 할당 모달 토글"""
    triggered_id = ctx.triggered_id
    if not triggered_id:
        raise PreventUpdate

    if triggered_id == "assign-btn" and assign_clicks:
        try:
            response = requests.get(f"{BASE_URL}/drivers")
            if response.status_code != 200:
                raise Exception("Failed to fetch drivers")

            drivers_data = response.json().get('data', {}).get('drivers', [])
            driver_options = [
                {"label": driver['driver_name'], "value": driver['driver']}
                for driver in drivers_data
            ]

            return True, f"{len(selected_rows)}건", driver_options
        except Exception as e:
            logger.error(f"Error fetching drivers: {e}")
            return True, "오류 발생", []

    elif triggered_id == "close-assign-modal":
        return False, no_update, no_update

    raise PreventUpdate


@callback(
    [Output('driver-assign-toast', 'is_open'),
     Output('driver-assign-toast', 'children'),
     Output('assign-modal', 'is_open', allow_duplicate=True),
     Output('dashboard-table', 'data', allow_duplicate=True)],
    [Input('confirm-assign', 'n_clicks')],
    [State('driver-select', 'value'),
     State('dashboard-table', 'selected_rows'),
     State('dashboard-table', 'data')],
    prevent_initial_call=True
)
def confirm_driver_assignment(n_clicks, driver_id, selected_rows, current_data):
    """기사 할당 확인"""
    if not n_clicks or not driver_id or not selected_rows:
        raise PreventUpdate

    try:
        delivery_ids = [current_data[idx]['dps'] for idx in selected_rows]
        response = requests.post(
            f"{BASE_URL}/driver/assign",
            json={
                'delivery_ids': delivery_ids,
                'driver_id': driver_id
            }
        )

        if response.status_code == 200:
            data_response = requests.get(f"{BASE_URL}/data")
            if data_response.status_code == 200:
                updated_data = data_response.json().get('data', {}).get('data', current_data)
                return True, "기사가 할당되었습니다.", False, updated_data
            return True, "기사가 할당되었습니다.", False, current_data

        error_msg = response.json().get('message', '기사 할당에 실패했습니다.')
        return True, error_msg, True, current_data

    except Exception as e:
        logger.error(f"Error in driver assignment: {e}")
        return True, f"기사 할당 중 오류 발생: {str(e)}", True, current_data


@callback(
    Output('dashboard-table', 'data', allow_duplicate=True),
    [Input('department-filter', 'value'),
     Input('status-filter', 'value'),
     Input('driver-filter', 'value'),
     Input('search-input', 'value'),
     Input('dashboard-table', 'page_current'),
     Input('refresh-btn', 'n_clicks')],
    [State('dashboard-table', 'data')],
    prevent_initial_call=True
)
def update_table_data(department, status, driver, search, page_current, n_clicks, current_data):
    """테이블 데이터 업데이트"""
    triggered_id = ctx.triggered_id
    if not ctx.triggered:
        raise PreventUpdate

    try:
        # 새로고침 버튼 클릭 시
        if triggered_id == 'refresh-btn' and n_clicks:
            refresh_response = requests.post(f"{BASE_URL}/refresh")
            if refresh_response.status_code != 200:
                logger.error("Failed to refresh dashboard data")
                return current_data or []

        filters = {
            'department': department if department != 'all' else None,
            'status': status if status != 'all' else None,
            'driver': driver if driver != 'all' else None,
            'search': search,
            'page': page_current + 1 if page_current else 1
        }

        response = requests.get(f"{BASE_URL}/data", params=filters)
        if response.status_code == 200:
            return response.json().get('data', {}).get('data', [])

    except Exception as e:
        logger.error(f"Error updating table: {e}")

    return current_data or []


@callback(
    [Output('status-update-toast', 'is_open'),
     Output('status-update-toast', 'children'),
     Output('detail-modal', 'is_open', allow_duplicate=True),
     Output('dashboard-table', 'data', allow_duplicate=True)],
    [Input('status-update-btn', 'n_clicks')],
    [State('status-select', 'value'),
     State('modal-dps', 'children'),
     State('dashboard-table', 'data')],
    prevent_initial_call=True
)
def update_delivery_status(n_clicks, new_status, delivery_id, current_data):
    """배송 상태 업데이트"""
    if not n_clicks or not delivery_id:
        raise PreventUpdate

    try:
        response = requests.put(
            f"{BASE_URL}/status",
            json={
                'delivery_id': delivery_id,
                'new_status': new_status
            }
        )

        if response.status_code == 200:
            data_response = requests.get(f"{BASE_URL}/data")
            if data_response.status_code == 200:
                updated_data = data_response.json().get('data', {}).get('data', current_data)
                return True, "상태가 업데이트되었습니다.", False, updated_data

            return True, "상태가 업데이트되었습니다.", False, current_data

        error_msg = response.json().get('message', '상태 업데이트에 실패했습니다.')
        return True, error_msg, True, current_data

    except Exception as e:
        logger.error(f"Error in status update: {e}")
        return True, f"상태 업데이트 중 오류 발생: {str(e)}", True, current_data


@callback(
    Output('assign-btn', 'disabled'),
    [Input('dashboard-table', 'selected_rows')]
)
def toggle_assign_button(selected_rows):
    """기사 할당 버튼 활성화/비활성화"""
    return not (selected_rows and len(selected_rows) > 0)