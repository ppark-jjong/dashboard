# src/dash_view/callbacks.py
from pydoc import html

from src.service.dashboard_service import DashboardService
from dash import Input, Output, State, callback, html
import dash_bootstrap_components as dbc
# 서비스 인스턴스 생성
service = DashboardService()
def create_detail_content(detail_data):
    """상세 정보 모달의 내용을 생성하는 함수"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                create_detail_field("부서", detail_data.get('department', '-')),
                create_detail_field("유형", detail_data.get('type', '-')),
                create_detail_field("창고", detail_data.get('warehouse', '-')),
                create_detail_field("기사명", detail_data.get('driver_name', '-')),
                create_detail_field("DPS", detail_data.get('dps', '-')),
                create_detail_field("SLA", detail_data.get('sla', '-')),
                create_detail_field("ETA", detail_data.get('eta', '-')),
            ], width=6),
            dbc.Col([
                create_detail_field("상태", detail_data.get('status', '-')),
                create_detail_field("주소", detail_data.get('address', '-')),
                create_detail_field("고객명", detail_data.get('customer', '-')),
                create_detail_field("연락처", detail_data.get('contact', '-')),
                create_detail_field("비고", detail_data.get('remark', '-')),
                create_detail_field("출발시간", detail_data.get('depart_time', '-')),
                create_detail_field("소요시간", f"{detail_data.get('duration_time', 0)}분"),
            ], width=6),
        ])
    ])

def create_detail_field(label, value):
    """상세 정보의 각 필드를 생성하는 헬퍼 함수"""
    return html.Div([
        html.Label(label, className="fw-bold mb-1"),
        html.Div(value, className="mb-3")
    ])

# 데이터 로딩 콜백
@callback(
    Output('dashboard-table', 'data'),
    [Input('refresh-interval', 'n_intervals'),
     Input('department-filter', 'value'),
     Input('status-filter', 'value'),
     Input('driver-filter', 'value'),
     Input('search-input', 'value')]
)
def update_table(n_intervals, department, status, driver, search):
    try:
        data = service.get_dashboard_data()
        return data['table_data']
    except Exception as e:
        print(f"Error loading data: {e}")
        return []


# 상세 정보 모달 콜백
@callback(
    [Output('detail-modal', 'is_open'),
     Output('modal-content', 'children')],
    [Input('dashboard-table', 'active_cell')],
    [State('dashboard-table', 'data')]
)
def show_details(active_cell, data):
    if active_cell:
        row = data[active_cell['row']]
        detail_data = service.get_detail_data(row['dps'])
        return True, create_detail_content(detail_data)
    return False, None


# 상태 업데이트 콜백
@callback(
    [Output('notification-toast', 'is_open'),
     Output('notification-toast', 'children')],
    [Input('confirm-status-change', 'n_clicks')],
    [State('status-select', 'value'),
     State('dashboard-table', 'selected_rows'),
     State('dashboard-table', 'data')]
)
def update_status(n_clicks, new_status, selected_rows, data):
    if n_clicks and selected_rows:
        try:
            for idx in selected_rows:
                dps = data[idx]['dps']
                service.update_delivery_status(dps, new_status)
            return True, "상태가 성공적으로 업데이트되었습니다."
        except Exception as e:
            return True, f"상태 업데이트 실패: {str(e)}"
    return False, ""


# 기사 필터 옵션 로딩 콜백
@callback(
    Output('driver-filter', 'options'),
    [Input('refresh-interval', 'n_intervals')]
)
def update_driver_options(n_intervals):
    try:
        drivers = service.get_drivers()
        options = [{"label": "전체", "value": "all"}]
        options.extend([{"label": d['driver_name'], "value": d['driver_name']} for d in drivers])
        return options
    except Exception as e:
        print(f"Error loading drivers: {e}")
        return [{"label": "전체", "value": "all"}]
