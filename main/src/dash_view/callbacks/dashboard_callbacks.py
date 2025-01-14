# src/dash_view/callbacks/dashboard_callbacks.py
from dash import Input, Output, State, callback
from flask import current_app
from dash.exceptions import PreventUpdate
import requests
import json
import logging

logger = logging.getLogger(__name__)


def get_base_url():
    return "http://127.0.0.1:5000/api/dashboard"


def init_callbacks(app):
    """콜백 초기화"""

    @app.callback(
        Output('dashboard-table', 'data'),
        Input('refresh-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def refresh_data(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        try:
            base_url = get_base_url()
            response = requests.get(f'{base_url}/data')
            if response.status_code == 200:
                response_data = response.json()
                if response_data['status'] == 'success':
                    return response_data['data']['data']
                logger.error(f"API error: {response_data.get('message', 'Unknown error')}")
                return []
            logger.error(f"Failed to get data: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error in refresh callback: {e}")
            return []

    @app.callback(
        Output('dashboard-table', 'data', allow_duplicate=True),
        [Input('department-filter', 'value'),
         Input('status-filter', 'value'),
         Input('search-input', 'value')],
        prevent_initial_call=True
    )
    def update_table_data(department, status, search):
        try:
            params = {
                'department': department if department != 'all' else None,
                'status': status if status != 'all' else None,
                'search': search,
                'page': 1,
                'page_size': 15
            }

            response = requests.get(f'{get_base_url()}/data', params=params)
            if response.status_code == 200:
                return response.json().get('data', {}).get('data', [])
            logger.error(f"Failed to get data: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error in update table callback: {e}")
            return []

    @app.callback(
        [Output('detail-modal', 'is_open'),
         Output('modal-dps', 'children'),
         Output('status-select', 'value')],
        Input('dashboard-table', 'active_cell'),
        State('dashboard-table', 'data'),
        prevent_initial_call=True
    )
    def show_detail_modal(active_cell, data):
        if not active_cell:
            raise PreventUpdate

        row = data[active_cell['row']]
        return True, row['dps'], row['status']

    @app.callback(
        [Output('notification-toast', 'is_open'),
         Output('notification-toast', 'header'),
         Output('notification-toast', 'children')],
        Input('status-update-btn', 'n_clicks'),
        [State('status-select', 'value'),
         State('modal-dps', 'children')],
        prevent_initial_call=True
    )
    def update_status(n_clicks, new_status, dps):
        if not n_clicks or not new_status or not dps:
            raise PreventUpdate

        try:
            response = requests.put(
                f'{get_base_url()}/status',
                json={'dps': dps, 'new_status': new_status}
            )

            if response.status_code == 200:
                return True, "상태 업데이트", "상태가 성공적으로 업데이트되었습니다."
            return True, "오류", "상태 업데이트에 실패했습니다."
        except Exception as e:
            logger.error(f"Error in status update callback: {e}")
            return True, "오류", f"오류 발생: {str(e)}"

    @app.callback(
        Output('assign-btn', 'disabled'),
        Input('dashboard-table', 'selected_rows')
    )
    def update_assign_button(selected_rows):
        return not selected_rows

    @app.callback(
        [Output('notification-toast', 'is_open', allow_duplicate=True),
         Output('notification-toast', 'header', allow_duplicate=True),
         Output('notification-toast', 'children', allow_duplicate=True)],
        Input('assign-btn', 'n_clicks'),
        [State('driver-filter', 'value'),
         State('dashboard-table', 'selected_rows'),
         State('dashboard-table', 'data')],
        prevent_initial_call=True
    )
    def assign_driver(n_clicks, driver_id, selected_rows, data):
        if not n_clicks or not driver_id or not selected_rows or driver_id == 'all':
            raise PreventUpdate

        try:
            selected_dps = [data[idx]['dps'] for idx in selected_rows]
            response = requests.post(
                f'{get_base_url()}/driver/assign',
                json={'dps_list': selected_dps, 'driver_id': driver_id}
            )

            if response.status_code == 200:
                return True, "기사 할당", "기사 할당이 완료되었습니다."
            return True, "오류", "기사 할당에 실패했습니다."
        except Exception as e:
            logger.error(f"Error in driver assign callback: {e}")
            return True, "오류", f"오류 발생: {str(e)}"

    return app
