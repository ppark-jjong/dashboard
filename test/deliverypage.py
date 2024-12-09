import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

# 정적 데이터
delivery_data = pd.DataFrame([
    {'Department': 'Logistics', 'Delivery': '김철수', 'DPS': 1010, 'ETA': '2024-12-10 14:00',
     'SLA': '4HR', 'Address': '서울특별시 강남구', 'Status': '완료', 'Recipient': '이영희'},
    {'Department': 'Logistics', 'Delivery': '박영수', 'DPS': 2020, 'ETA': '2024-12-10 16:00',
     'SLA': '6HR', 'Address': '경기도 수원시', 'Status': '진행중', 'Recipient': '최수진'}
])

# Dash 앱 초기화
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 레이아웃
app.layout = dbc.Container([
    html.H1("배송 현황 시트", className="text-center my-4"),
    dbc.Table.from_dataframe(delivery_data, id='delivery-table', bordered=True, hover=True, responsive=True),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("배송 상세 정보")),
        dbc.ModalBody(id="modal-body"),
        dbc.ModalFooter(dbc.Button("닫기", id="close-modal", className="ms-auto", n_clicks=0))
    ], id="detail-modal", size="lg")
], fluid=True, style={'maxWidth': '90%'})

# 콜백 (행 클릭 시 모달 표시)
@app.callback(
    [Output("detail-modal", "is_open"),
     Output("modal-body", "children")],
    [Input({'type': 'row', 'index': dash.ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def show_modal(n_clicks):
    if not n_clicks:
        return False, None
    return True, "선택한 배송의 상세 정보"

if __name__ == '__main__':
    app.run_server(debug=True)
