from dash import Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate
import requests
import logging

logger = logging.getLogger(__name__)
BASE_URL = 'http://localhost:5000/api'


@callback(
    Output('dashboard-table', 'data'),
    [Input('department-filter', 'value'),
     Input('status-filter', 'value'),
     Input('driver-filter', 'value'),
     Input('search-input', 'value'),
     Input('dashboard-table', 'page_current'),
     Input('refresh-btn', 'n_clicks')],
    prevent_initial_call=True
)
def update_table(department, status, driver, search, page_current, n_clicks):
    """테이블 데이터 업데이트"""
    try:
        params = {
            'department': department if department != 'all' else None,
            'status': status if status != 'all' else None,
            'driver': driver if driver != 'all' else None,
            'search': search,
            'page': page_current + 1 if page_current else 1
        }

        response = requests.get(f"{BASE_URL}/dashboard/data", params=params)
        if response.status_code == 200:
            return response.json()['data']['data']
        return []
    except Exception as e:
        logger.error(f"Error updating table: {e}")
        return []


@callback(
    [Output('assign-btn', 'disabled'),
     Output('selected-rows', 'children')],
    [Input('dashboard-table', 'selected_rows')]
)
def toggle_assign_button(selected_rows):
    """기사 할당 버튼 상태 관리"""
    if not selected_rows:
        return True, "0건 선택"
    return False, f"{len(selected_rows)}건 선택"


@callback(
    [Output('status-update-toast', 'is_open'),
     Output('status-update-toast', 'children')],
    [Input('status-update-btn', 'n_clicks')],
    [State('status-select', 'value'),
     State('detail-modal', 'dps')]
)
def update_status(n_clicks, new_status, dps):
    """상태 업데이트"""
    if not n_clicks or not new_status or not dps:
        raise PreventUpdate

    try:
        response = requests.put(
            f"{BASE_URL}/dashboard/status",
            json={'dps': dps, 'new_status': new_status}
        )

        if response.status_code == 200:
            return True, "상태가 성공적으로 업데이트되었습니다."
        return True, "상태 업데이트에 실패했습니다."
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        return True, f"오류 발생: {str(e)}"


@callback(
    Output('driver-filter', 'options'),
    Input('refresh-btn', 'n_clicks')
)
def update_driver_options(n_clicks):
    """기사 필터 옵션 업데이트"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard/drivers")
        if response.status_code == 200:
            drivers = response.json()['data']['drivers']
            options = [{"label": "전체", "value": "all"}]
            options.extend([
                {"label": driver['driver_name'], "value": driver['driver']}
                for driver in drivers
            ])
            return options
        return [{"label": "전체", "value": "all"}]
    except Exception as e:
        logger.error(f"Error updating driver options: {e}")
        return [{"label": "전체", "value": "all"}]