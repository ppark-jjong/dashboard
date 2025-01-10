# src/dash_view/dashboard_callbacks.py
from dash import Input, Output, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate
import logging
import requests
from urllib.parse import urlencode
from src.repository.redis_repository import RedisRepository

logger = logging.getLogger(__name__)
BASE_URL = 'http://localhost:5000/api/dashboard'
redis_repo = RedisRepository()


# src/dash_view/dashboard_callbacks.py

@callback(
    Output('dashboard-table', 'data'),
    [Input('department-filter', 'value'),
     Input('status-filter', 'value'),
     Input('driver-filter', 'value'),
     Input('search-input', 'value'),
     Input('dashboard-table', 'page_current')],
    [State('dashboard-table', 'data')],
    prevent_initial_call=True
)
def update_table_data(department, status, driver, search, page_current, current_data):
    """테이블 데이터 업데이트 (필터링)"""
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered_id

    # 기사 필터의 경우 캐시된 데이터 활용
    if driver and driver != 'all':
        try:
            response = requests.get(f"{BASE_URL}/drivers")
            if response.status_code == 200:
                drivers_data = response.json().get('drivers', [])
                # 캐시된 기사 정보로 필터링
        except Exception as e:
            logger.error(f"Error fetching drivers: {e}")

    # 나머지 필터 처리
    try:
        filters = {
            'department': department if department != 'all' else None,
            'status': status if status != 'all' else None,
            'driver': driver if driver != 'all' else None,
            'search': search
        }

        response = requests.get(
            f"{BASE_URL}/data",
            params={**filters, 'page': page_current + 1 if page_current else 1}
        )

        if response.status_code == 200:
            return response.json().get('data', [])

    except Exception as e:
        logger.error(f"Error updating table: {e}")

    return current_data or []


@callback(
    Output('driver-filter', 'options'),
    Input('refresh-btn', 'n_clicks')
)
def update_driver_filter(n_clicks):
    # Redis에서 직접 조회
    cached_drivers = redis_repo.get_drivers()
    if cached_drivers:
        options = [{"label": "전체", "value": "all"}]
        options.extend([
            {"label": driver['driver_name'], "value": driver['driver']}
            for driver in cached_drivers
        ])
        return options

    return [{"label": "전체", "value": "all"}]


@callback(
    [Output('assign-modal', 'is_open'),
     Output('selected-count', 'children'),
     Output('driver-select', 'options')],
    [Input('assign-btn', 'n_clicks'),
     Input('close-assign-modal', 'n_clicks')],
    [State('dashboard-table', 'selected_rows'),
     State('dashboard-table', 'data'),
     State('assign-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_assign_modal(assign_clicks, close_clicks, selected_rows, data, is_open):
    """기사할당 모달 토글"""
    triggered_id = ctx.triggered_id
    if not triggered_id:
        raise PreventUpdate

    if triggered_id == "assign-btn" and assign_clicks:
        try:
            response = requests.get(f"{BASE_URL}/drivers")
            if response.status_code != 200:
                raise Exception("Failed to fetch drivers")

            drivers_data = response.json()
            driver_options = [
                {"label": f"{driver['driver_name']} ({driver['driver_region']})",
                 "value": driver['driver']}
                for driver in drivers_data.get('drivers', [])
            ]

            selected_count = f"{len(selected_rows)}건"
            return True, selected_count, driver_options
        except Exception as e:
            logger.error(f"Error fetching drivers: {str(e)}")
            return True, "오류 발생", []
    elif triggered_id == "close-assign-modal":
        return False, no_update, no_update

    raise PreventUpdate


@callback(
    [Output('driver-assign-toast', 'is_open'),
     Output('driver-assign-toast', 'children'),
     Output('driver-assign-toast', 'color'),
     Output('assign-modal', 'is_open', allow_duplicate=True),
     Output('dashboard-table', 'data', allow_duplicate=True)],
    Input('confirm-assign', 'n_clicks'),
    [State('driver-select', 'value'),
     State('dashboard-table', 'selected_rows'),
     State('dashboard-table', 'data')],
    prevent_initial_call=True
)
def confirm_driver_assignment(n_clicks, driver_id, selected_rows, data):
    """기사 할당 확인"""
    if not n_clicks or not driver_id or not selected_rows:
        raise PreventUpdate

    try:
        delivery_ids = [data[idx]['dps'] for idx in selected_rows]
        response = requests.post(
            f"{BASE_URL}/driver/assign",
            json={
                'delivery_ids': delivery_ids,
                'driver_id': driver_id
            }
        )

        if response.status_code == 200:
            # 테이블 데이터 새로고침을 위한 API 호출
            data_response = requests.get(f"{BASE_URL}/data")
            if data_response.status_code == 200:
                updated_data = data_response.json().get('data', {}).get('table_data', data)
            else:
                updated_data = data

            return True, f"{len(delivery_ids)}건의 배송이 기사에게 할당되었습니다.", "success", False, updated_data
        else:
            error_msg = response.json().get('message', '기사 할당에 실패했습니다.')
            return True, error_msg, "danger", no_update, no_update

    except Exception as e:
        logger.error(f"Error in driver assignment: {str(e)}")
        return True, f"기사 할당 중 오류 발생: {str(e)}", "danger", no_update, no_update


@callback(
    [Output("detail-modal", "is_open"),
     Output("modal-department", "children"),
     Output("modal-type", "children"),
     Output("modal-warehouse", "children"),
     Output("modal-driver_name", "children"),
     Output("modal-dps", "children"),
     Output("modal-sla", "children"),
     Output("status-select", "value"),
     Output("modal-eta", "children"),
     Output("modal-address", "children"),
     Output("modal-customer", "children"),
     Output("modal-contact", "children"),
     Output("modal-remark", "children"),
     Output("modal-depart_time", "children"),
     Output("modal-duration_time", "children")],
    [Input("dashboard-table", "active_cell"),
     Input("close-modal", "n_clicks")],
    [State("dashboard-table", "data"),
     State("detail-modal", "is_open")]
)
def toggle_modal(active_cell, close_clicks, data, is_open):
    ctx_msg = ctx.triggered_id
    if ctx_msg == "close-modal":
        return False, *([no_update] * 14)  # 수정된 Output 개수에 맞게 조정

    if active_cell and data:
        row = data[active_cell['row']]
        return (True,  # modal is_open
                row.get('department', '-'),  # department
                row.get('type', '-'),  # type
                row.get('warehouse', '-'),  # warehouse
                row.get('driver_name', '-'),  # driver_name
                row.get('dps', '-'),  # dps
                row.get('sla', '-'),  # sla
                row.get('status', '대기'),  # status_select value
                row.get('eta', '-'),  # eta
                row.get('address', '-'),  # address
                row.get('customer', '-'),  # customer
                row.get('contact', '-'),  # contact
                row.get('remark', '-'),  # remark
                row.get('depart_time', '-'),  # depart_time
                row.get('duration_time', '-'))  # duration_time

    return False, *([no_update] * 14)


@callback(
    [Output('status-update-toast', 'is_open'),
     Output('status-update-toast', 'children'),
     Output('status-update-toast', 'color'),
     Output('detail-modal', 'is_open', allow_duplicate=True),
     Output('dashboard-table', 'data', allow_duplicate=True)],
    [Input('status-update-btn', 'n_clicks')],
    [State('status-select', 'value'),
     State('detail-dps', 'children'),
     State('dashboard-table', 'data')],
    prevent_initial_call=True
)
def update_delivery_status(n_clicks, new_status, delivery_id, table_data):
    """상세 정보 모달에서 상태 업데이트"""
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
            # 테이블 데이터 업데이트
            updated_data = [
                {**row, 'status': new_status} if row['dps'] == delivery_id else row
                for row in table_data
            ]
            return True, "상태가 성공적으로 업데이트되었습니다.", "success", False, updated_data
        else:
            error_msg = response.json().get('message', '상태 업데이트에 실패했습니다.')
            return True, error_msg, "danger", no_update, no_update

    except Exception as e:
        logger.error(f"Error in status update: {str(e)}")
        return True, f"상태 업데이트 중 오류 발생: {str(e)}", "danger", no_update, no_update


@callback(
    Output('assign-btn', 'disabled'),
    [Input('dashboard-table', 'selected_rows')]
)
def toggle_assign_button(selected_rows):
    """기사 할당 버튼 활성화/비활성화"""
    return not (selected_rows and len(selected_rows) > 0)
