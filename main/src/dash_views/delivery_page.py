from dash import html, callback, Input, Output, State
import data_generator as dg
from components import create_data_table

def create_delivery_page():
    """배송 현황 페이지 생성"""
    df = dg.generate_delivery_data()

    return html.Div([
        html.H2('배송 현황', className='mb-4'),

        # 데이터 테이블
        create_data_table(df, 'delivery'),

        # 모달
        html.Div(
            id='delivery-modal',
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
                                        html.H5('배송 상세 정보', className='modal-title'),
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
                                                html.Span(id='modal-delivery-id')
                                            ], className='mb-3'),
                                            html.Div([
                                                html.Strong('운송타입: '),
                                                html.Span(id='modal-operation-type')
                                            ], className='mb-3'),
                                            html.Div([
                                                html.Strong('부서: '),
                                                html.Span(id='modal-department')
                                            ], className='mb-3'),
                                            html.Div([
                                                html.Strong('DPS 번호: '),
                                                html.Span(id='modal-dps')
                                            ], className='mb-3'),
                                            html.Div([
                                                html.Strong('SLA: '),
                                                html.Span(id='modal-sla')
                                            ], className='mb-3'),
                                            html.Div([
                                                html.Strong('ETA: '),
                                                html.Span(id='modal-eta')
                                            ], className='mb-3'),
                                            html.Div([
                                                html.Strong('상태: '),
                                                html.Span(id='modal-status')
                                            ], className='mb-3'),
                                        ])
                                    ]
                                ),
                                html.Div(
                                    className='modal-footer',
                                    children=[
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
        Output('modal-delivery-id', 'children'),
        Output('modal-operation-type', 'children'),
        Output('modal-department', 'children'),
        Output('modal-dps', 'children'),
        Output('modal-sla', 'children'),
        Output('modal-eta', 'children'),
        Output('modal-status', 'children')
    ],
    Input('delivery-table', 'active_cell'),
    State('delivery-table', 'data'),
    prevent_initial_call=True
)
def update_delivery_modal(active_cell, table_data):
    """선택된 행 데이터를 모달에 표시"""
    if not active_cell:
        return [None] * 7

    row = table_data[active_cell['row']]
    return (
        row['DeliveryID'],
        row['OperationType'],
        row['Department'],
        row['DPS'],
        row['SLA'],
        row['ETA'],
        row['Status']
    )
