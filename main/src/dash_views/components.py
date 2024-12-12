# components.py
from dash import html, dcc, dash_table
import plotly.express as px


def create_navbar():
    """네비게이션 바 컴포넌트"""
    return html.Nav(
        className='navbar navbar-expand-lg navbar-light bg-white shadow-sm sticky-top',
        children=[
            html.Div([
                html.Span([
                    html.I(className='fas fa-truck me-2'),
                    'Smart Delivery'
                ], className='navbar-brand fw-bold'),
                html.Div([
                    dcc.Link(
                        html.Div([
                            html.I(className='fas fa-chart-line me-2'),
                            '요약'
                        ]),
                        href='/',
                        className='nav-link mx-3'
                    ),
                    dcc.Link(
                        html.Div([
                            html.I(className='fas fa-box me-2'),
                            '배송'
                        ]),
                        href='/delivery',
                        className='nav-link mx-3'
                    ),
                    dcc.Link(
                        html.Div([
                            html.I(className='fas fa-users me-2'),
                            '배차'
                        ]),
                        href='/dispatch',
                        className='nav-link mx-3'
                    ),
                ], className='navbar-nav ms-auto')
            ], className='container-fluid px-4')
        ]
    )


def create_stats_card(title, value, icon=None, color='primary'):
    """통계 카드 컴포넌트"""
    colors = {
        'primary': '#FFB3B3',
        'secondary': '#B3D9FF',
        'warning': '#FFE5B3',
        'success': '#B3FFB3'
    }

    return html.Div(
        className='stats-card p-4 rounded-3 shadow-sm',
        style={'backgroundColor': colors.get(color, colors['primary'])},
        children=[
            html.Div([
                html.I(className=f'{icon} fa-2x mb-2', style={'color': '#4a5568'}) if icon else None,
                html.H6(title, className='text-muted mb-2', style={'color': '#4a5568'}),
                html.H4(value, className='mb-0 fw-bold', style={'color': '#2d3748'})
            ], className='text-center')
        ]
    )


def create_data_table(df, id_prefix):
    """데이터 테이블 컴포넌트"""
    return html.Div([
        # 필터링 섹션
        html.Div(className='filter-container', children=[
            html.Div(className='filter-section', children=[
                # 검색창
                dcc.Input(
                    id=f'{id_prefix}-search',
                    type='text',
                    placeholder='검색어를 입력하세요',
                    className='form-control filter-item'
                ),
                # ETA 필터
                dcc.Dropdown(
                    id=f'{id_prefix}-eta-filter',
                    options=[
                        {'label': '전체 시간', 'value': ''},
                        {'label': '1시간 이내', 'value': '1'},
                        {'label': '3시간 이내', 'value': '3'},
                        {'label': '6시간 이내', 'value': '6'}
                    ],
                    value='',
                    placeholder='ETA 필터',
                    className='filter-item'
                ),
                # SLA 필터
                dcc.Dropdown(
                    id=f'{id_prefix}-sla-filter',
                    options=[
                        {'label': '전체 SLA', 'value': ''},
                        {'label': '일반', 'value': '일반'},
                        {'label': '프리미엄', 'value': '프리미엄'},
                        {'label': '익일', 'value': '익일'}
                    ],
                    value='',
                    placeholder='SLA 필터',
                    className='filter-item'
                ),
                # 부서 필터
                dcc.Dropdown(
                    id=f'{id_prefix}-department-filter',
                    options=[
                        {'label': '전체 부서', 'value': ''},
                        {'label': '물류1팀', 'value': '물류1팀'},
                        {'label': '물류2팀', 'value': '물류2팀'},
                        {'label': '물류3팀', 'value': '물류3팀'},
                        {'label': '특송팀', 'value': '특송팀'}
                    ],
                    value='',
                    placeholder='부서 필터',
                    className='filter-item'
                ),
                # 새로고침 버튼
                html.Button(
                    children=[
                        html.I(className='fas fa-sync-alt me-2'),
                        '새로고침'
                    ],
                    id=f'{id_prefix}-refresh',
                    className='btn btn-primary refresh-btn'
                ),
            ])
        ]),

        # 데이터 테이블
        html.Div(className='data-table-container', children=[
            dash_table.DataTable(
                id=f'{id_prefix}-table',
                data=df.to_dict('records'),
                columns=[{"name": col, "id": col} for col in df.columns],

                # 페이지네이션 설정
                page_action='native',
                page_current=0,
                page_size=15,

                # 정렬 설정
                sort_action='native',
                sort_mode='multi',

                # 선택 설정
                cell_selectable=True,
                row_selectable=False,

                # 스타일 설정
                style_table={
                    'width': '100%'
                },

                # 셀 스타일
                style_cell={
                    'textAlign': 'center',
                    'padding': '12px',
                    'fontFamily': 'system-ui, -apple-system, sans-serif',
                    'fontSize': '14px',
                    'color': '#475569',
                    'cursor': 'pointer',
                    'height': 'auto',
                    'minWidth': '100px',
                    'maxWidth': '180px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },

                # 헤더 스타일
                style_header={
                    'backgroundColor': '#f1f5f9',
                    'fontWeight': '600',
                    'textAlign': 'center',
                    'padding': '16px 12px',
                    'borderBottom': '2px solid #e2e8f0'
                },

                # 데이터 셀 스타일
                style_data={
                    'backgroundColor': 'white',
                    'borderBottom': '1px solid #e2e8f0',
                },

                # 조건부 스타일
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8fafc',
                    },

                    {
                        # 선택된 셀이 있는 행 전체 스타일
                        'if': {
                            'state': 'active'
                        },
                        'backgroundColor': '#e2e8f0',
                        'border': '1px solid #cbd5e1'
                    }
                ],

                # CSS 클래스
                css=[
                    # 행 호버 효과
                    {
                        'selector': 'tr:hover',
                        'rule': 'background-color: #f1f5f9 !important'
                    },
                    # 선택된 행 스타일
                    {
                        'selector': '.dash-cell-value.focused',
                        'rule': 'background-color: #e2e8f0 !important; border: 1px solid #cbd5e1 !important;'
                    }
                ],

                # 툴팁
                tooltip_delay=0,
                tooltip_duration=None,
                tooltip_data=[
                    {
                        column: {'value': '클릭하여 상세 정보 보기', 'type': 'text'}
                        for column in df.columns
                    }
                    for _ in range(len(df))
                ],

                # 특정 컬럼 너비 조정
                style_cell_conditional=[
                    {'if': {'column_id': 'DPS'}, 'minWidth': '120px'},
                    {'if': {'column_id': 'Address'}, 'minWidth': '250px'},
                    {'if': {'column_id': 'ETA'}, 'minWidth': '150px'},
                ]
            )
        ]),

        # 행 선택 상태를 저장하기 위한 Store 컴포넌트
        dcc.Store(id=f'{id_prefix}-selected-row-index')
    ])

def create_modal(id_prefix, title, content=None, has_footer=True):
    """모달 컴포넌트"""
    footer = html.Div(
        className='modal-footer',
        children=[
            html.Button(
                '닫기',
                className='btn btn-secondary',
                **{'data-bs-dismiss': 'modal'}
            )
        ]
    ) if has_footer else None

    return html.Div(
        id=f'{id_prefix}-modal',
        className='modal fade',
        children=[
            html.Div(
                className='modal-dialog modal-lg',
                children=[
                    html.Div(
                        className='modal-content',
                        children=[
                            # 모달 헤더
                            html.Div(
                                className='modal-header',
                                children=[
                                    html.H5(title, className='modal-title'),
                                    html.Button(
                                        '×',
                                        className='btn-close',
                                        **{'data-bs-dismiss': 'modal'}
                                    )
                                ]
                            ),
                            # 모달 본문
                            html.Div(
                                className='modal-body',
                                children=content if content else []
                            ),
                            # 모달 푸터 (옵션)
                            footer
                        ]
                    )
                ]
            )
        ]
    )


def create_pie_chart(data, values, names, title):
    """파이 차트 컴포넌트"""
    fig = px.pie(
        data,
        values=values,
        names=names,
        title=title,
        hole=0.4,
        color_discrete_sequence=['#FFB3B3', '#B3D9FF', '#FFE5B3', '#B3FFB3']
    )

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(t=60, b=20, l=20, r=20),
        title={
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16}
        },
        showlegend=True,
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.2,
            'xanchor': 'center',
            'x': 0.5
        }
    )

    return html.Div(
        className='chart-container bg-white rounded-3 p-3 shadow-sm',
        children=[
            dcc.Graph(
                figure=fig,
                config={'displayModeBar': False}
            )
        ]
    )