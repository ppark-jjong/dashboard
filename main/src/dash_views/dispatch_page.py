from dash import html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate

import data_generator as dg
from components import create_data_table

def create_dispatch_page():
    """배차 관리 페이지 생성"""
    df = dg.generate_delivery_data()
    drivers = dg.get_available_drivers()

    return html.Div([
        html.H2('배차 관리', className='mb-4'),

        # 데이터 테이블
        create_data_table(df, 'dispatch'),

        # 모달
        html.Div(
            id='dispatch-modal',
            className='modal fade',
            children=[
                html.Div(
                    className='modal-dialog modal-lg',
                    children=[
                        html.Div(
                            className='modal-content',
                            children=[
                                html.Div(
                                    className='modal-header',
                                    children=[
                                        html.H5('배차 상세 정보', className='modal-title'),
                                        html.Button(
                                            '×',
                                            className='btn-close',
                                            **{'data-bs-dismiss': 'modal'}
                                        ),
                                    ]
                                ),
                                html.Div(
                                    className='modal-body',
                                    children=[
                                        html.Div([
                                            html.Div([
                                                html.Strong('배송번호: '),
                                                html.Span(id='modal-dispatch-delivery-id')
                                            ], className='mb-3'),
                                            html.Div([
                                                html.Strong('현재 기사: '),
                                                html.Span(id='modal-current-driver')
                                            ], className='mb-3'),
                                            html.Div([
                                                html.Strong('배송 상태: '),
                                                html.Span(id='modal-dispatch-status')
                                            ], className='mb-3'),
                                        ], className='mb-4'),

                                        html.Div([
                                            html.Label('기사 변경:', className='form-label'),
                                            dcc.Dropdown(
                                                id='modal-driver-dropdown',
                                                options=[
                                                    {'label': f"{d['name']} ({d['status']})", 'value': d['id']}
                                                    for d in drivers
                                                ],
                                                placeholder='기사를 선택하세요'
                                            )
                                        ], className='mb-4')
                                    ]
                                ),
                                html.Div(
                                    className='modal-footer',
                                    children=[
                                        html.Button(
                                            '저장',
                                            id='dispatch-save-btn',
                                            className='btn btn-primary'
                                        ),
                                        html.Button(
                                            '닫기',
                                            className='btn btn-secondary',
                                            **{'data-bs-dismiss': 'modal'}
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ])

@callback(
    [
        Output('dispatch-modal', 'className'),
        Output('modal-dispatch-delivery-id', 'children'),
        Output('modal-current-driver', 'children'),
        Output('modal-dispatch-status', 'children'),
        Output('modal-driver-dropdown', 'value')
    ],
    Input('dispatch-table', 'active_cell'),
    State('dispatch-table', 'data'),
    prevent_initial_call=True
)
def open_dispatch_modal(active_cell, table_data):
    """배차 모달 데이터 업데이트 및 열기"""
    if not active_cell:
        raise PreventUpdate

    row = table_data[active_cell['row']]
    return (
        'modal fade show',
        row['DeliveryID'],
        row['Driver'] or '미배정',
        row['Status'],
        row['Driver']
    )

@callback(
    Output('dispatch-table', 'data', allow_duplicate=True),
    Input('dispatch-save-btn', 'n_clicks'),
    [State('modal-driver-dropdown', 'value'),
     State('dispatch-table', 'active_cell'),
     State('dispatch-table', 'data')],
    prevent_initial_call=True
)
def save_dispatch_assignment(n_clicks, selected_driver, active_cell, table_data):
    """배차 데이터 저장"""
    if not n_clicks or not active_cell or not selected_driver:
        raise PreventUpdate

    table_data[active_cell['row']]['Driver'] = selected_driver
    dg.save_delivery_data(table_data)
    return table_data
