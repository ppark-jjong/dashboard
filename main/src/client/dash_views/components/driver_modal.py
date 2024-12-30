from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

# 기사 데이터 상수 정의
DRIVER_OPTIONS = [
    {'label': '김운송', 'value': '김운송'},
    {'label': '이배달', 'value': '이배달'},
    {'label': '박퀵서비스', 'value': '박퀵서비스'},
    {'label': '최배송', 'value': '최배송'},
    {'label': '정기사', 'value': '정기사'}
]


def create_driver_modal():
    """
    기사 할당 모달 컴포넌트 생성
    - 최적화된 상태 관리
    - 향상된 사용자 경험
    - 성능 최적화된 렌더링
    """
    return html.Div([
        # 모달 상태 관리를 위한 저장소
        dcc.Store(id='driver-modal-state'),

        # 기사 할당 모달
        dbc.Modal([
            dbc.ModalHeader([
                html.H5("기사 할당", className='modal-title'),
                html.Span(id='selected-count', className='selected-count')
            ], className='d-flex justify-content-between align-items-center'),

            dbc.ModalBody([
                # 기사 선택 섹션
                html.Div([
                    html.Label(
                        "배정할 기사 선택",
                        className='driver-select-label',
                        style={'marginBottom': '8px', 'display': 'block'}
                    ),
                    dcc.Dropdown(
                        id='driver-select',
                        options=DRIVER_OPTIONS,
                        multi=True,
                        placeholder='기사를 선택하세요',
                        className='driver-select-dropdown'
                    ),
                ], className='driver-select-container'),

                # 선택된 주문 목록
                html.Div([
                    html.Div(
                        "선택된 배송 건",
                        className='selected-orders-title'
                    ),
                    html.Div(
                        id='selected-orders',
                        className='selected-orders-list'
                    )
                ], className='selected-orders-container mt-4')
            ]),

            # 모달 푸터 - 액션 버튼
            dbc.ModalFooter([
                dbc.Button(
                    "취소",
                    id="close-driver-modal",
                    className="cancel-btn me-2",
                    color="secondary"
                ),
                dbc.Button(
                    "할당",
                    id="assign-driver",
                    className="assign-btn",
                    color="primary"
                )
            ])
        ],
            id='driver-modal',
            className='custom-modal driver-assignment-modal',
            backdrop="static"  # 모달 외부 클릭 방지
        )
    ])


# 콜백: 선택된 주문 표시 업데이트
@callback(
    [Output('selected-orders', 'children'),
     Output('selected-count', 'children')],
    [Input('delivery-table', 'selected_rows'),
     Input('delivery-table', 'data')]
)
def update_selected_orders(selected_rows, data):
    if not selected_rows:
        return None, None

    selected_data = [data[idx] for idx in selected_rows]
    count_text = f"선택된 건수: {len(selected_data)}건"

    orders_display = html.Div([
        html.Div(
            children=[
                html.Div([
                    html.Span(
                        row['dps'],
                        className='dps-number'
                    ),
                    html.Span(
                        row['address'][:30] + ('...' if len(row['address']) > 30 else ''),
                        className='address-text'
                    )
                ], className='order-item')
            ],
            className='order-item-container'
        )
        for row in selected_data
    ])

    return orders_display, count_text


# 콜백: 할당 버튼 상태 관리
@callback(
    Output('assign-driver', 'disabled'),
    [Input('driver-select', 'value')]
)
def toggle_assign_button(selected_drivers):
    return not selected_drivers


# 콜백: 모달 초기화
@callback(
    [Output('driver-select', 'value'),
     Output('driver-modal', 'is_open')],
    [Input('close-driver-modal', 'n_clicks'),
     Input('assign-driver', 'n_clicks')],
    [State('driver-modal', 'is_open')]
)
def reset_modal(n_close, n_assign, is_open):
    if n_close or n_assign:
        return None, False
    return dash.no_update, is_open