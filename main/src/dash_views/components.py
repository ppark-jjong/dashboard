# components.py
from dash import html, dcc, dash_table
import plotly.express as px


def create_data_table(df, id_prefix):
    """고급 데이터 테이블 컴포넌트"""
    return html.Div([
        # 컨트롤 바
        html.Div([
            html.Button(
                children=[
                    html.I(className='fas fa-sync-alt me-2'),
                    '새로고침'
                ],
                id=f'{id_prefix}-refresh',
                className='btn btn-primary'
            ),
            html.Div([
                dcc.Input(
                    id=f'{id_prefix}-search',
                    type='text',
                    placeholder='검색어를 입력하세요',
                    className='form-control me-2',
                    n_submit=0,
                    style={'width': '300px'}
                ),
                html.Button(
                    html.I(className='fas fa-search'),
                    id=f'{id_prefix}-search-btn',
                    className='btn btn-outline-primary'
                )
            ], className='d-flex')
        ], className='d-flex justify-content-between align-items-center mb-4'),

        # 데이터 테이블
        html.Div([
            dash_table.DataTable(
                id=f'{id_prefix}-table',
                data=df.to_dict('records'),
                columns=[
                    {"name": "OperationType", "id": "OperationType"},
                    {"name": "Department", "id": "Department"},
                    {"name": "DPS", "id": "DPS"},
                    {"name": "SLA", "id": "SLA"},
                    {"name": "ETA", "id": "ETA"},
                    {"name": "Address", "id": "Address"},
                    {"name": "Status", "id": "Status"},
                    {"name": "DepartTime", "id": "DepartTime"},
                    {"name": "Driver", "id": "Driver"},
                    {"name": "Recipient", "id": "Recipient"}
                ],

                # 페이지네이션 설정
                page_action='native',
                page_current=0,
                page_size=15,

                # 정렬
                sort_action='native',
                sort_mode='multi',

                # 테이블 기본 스타일
                style_table={
                    'width': '100%',
                    'border': '1px solid #e2e8f0',
                    'borderRadius': '8px',
                    'overflow': 'hidden',
                },

                # 헤더 스타일
                style_header={
                    'backgroundColor': '#f1f5f9',
                    'color': '#334155',
                    'fontWeight': '600',
                    'textAlign': 'center',  # 헤더 중앙 정렬
                    'padding': '12px 16px',
                    'borderBottom': '2px solid #e2e8f0',
                    'borderRight': '1px solid #e2e8f0',
                    'fontSize': '14px',
                },

                # 셀 기본 스타일
                style_cell={
                    'textAlign': 'center',  # 모든 셀 중앙 정렬
                    'padding': '12px 16px',
                    'fontSize': '14px',
                    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    'borderRight': '1px solid #e2e8f0',
                    'borderBottom': '1px solid #e2e8f0',
                },

                # 데이터 셀 스타일
                style_data={
                    'whiteSpace': 'nowrap',
                    'height': 'auto',
                    'lineHeight': '1.5',
                    'color': '#475569',
                    'backgroundColor': 'white',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },

                # 조건부 셀 스타일
                style_cell_conditional=[
                    {'if': {'column_id': 'OperationType'}, 'width': '100px'},
                    {'if': {'column_id': 'Department'}, 'width': '120px'},
                    {'if': {'column_id': 'DPS'}, 'width': '120px'},
                    {'if': {'column_id': 'SLA'}, 'width': '100px'},
                    {'if': {'column_id': 'ETA'}, 'width': '150px'},
                    {'if': {'column_id': 'Address'}, 'width': '400px', 'maxWidth': '400px'},
                    {'if': {'column_id': 'Status'}, 'width': '100px'},
                    {'if': {'column_id': 'DepartTime'}, 'width': '120px'},
                    {'if': {'column_id': 'Driver'}, 'width': '120px'},
                    {'if': {'column_id': 'Recipient'}, 'width': '120px'},
                ],

                # 조건부 데이터 스타일
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8fafc',
                    },
                    {
                        'if': {'state': 'selected'},
                        'backgroundColor': '#e2e8f0',
                        'border': '1px solid #cbd5e1',
                    },
                    {
                        'if': {'state': 'active'},
                        'backgroundColor': '#e2e8f0',
                        'border': '1px solid #cbd5e1',
                    }
                ],

                # CSS를 통한 페이지네이션 스타일링
                css=[{
                    'selector': '.dash-spreadsheet td div',
                    'rule': '''
                display: block !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                text-align: center !important;
                margin: 0 auto !important;
            '''
                }],
            )
        ], className='table-responsive shadow-sm')
    ], className='data-table-container bg-white rounded-3 p-4')


def create_stats_card(title, value, icon=None, color='primary'):
    """통계 카드 컴포넌트"""
    colors = {
        'primary': '#FFB3B3',  # 파스텔 빨간색
        'secondary': '#B3D9FF',  # 파스텔 파란색
        'warning': '#FFE5B3',  # 파스텔 노란색
        'success': '#B3FFB3'  # 파스텔 초록색
    }

    return html.Div(
        className=f'stats-card p-4 rounded-3 shadow-sm',
        style={'backgroundColor': colors.get(color, colors['primary'])},
        children=[
            html.Div([
                html.I(className=f'{icon} fa-2x mb-2', style={'color': '#4a5568'}) if icon else None,
                html.H6(title, className='text-muted mb-2', style={'color': '#4a5568'}),
                html.H4(value, className='mb-0 fw-bold', style={'color': '#2d3748'})
            ], className='text-center')
        ]
    )


def create_pie_chart(df, column, title):
    """파이 차트 컴포넌트"""
    status_counts = df[column].value_counts().reset_index()
    status_counts.columns = ['상태', '건수']

    colors = ['#FFB3B3', '#B3D9FF', '#FFE5B3', '#B3FFB3']  # 파스텔톤 색상

    fig = px.pie(
        status_counts,
        values='건수',
        names='상태',
        title=title,
        hole=0.4,
        color_discrete_sequence=colors
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="상태: %{label}<br>건수: %{value}<br>비율: %{percent}<extra></extra>"
    )

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        title={
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.95,
            'yanchor': 'top',
            'font': {
                'size': 16,
                'color': '#2d3748'
            }
        },
        margin=dict(t=60, b=20, l=20, r=20),
        showlegend=True,
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.2,
            'xanchor': 'center',
            'x': 0.5
        }
    )

    return html.Div([
        dcc.Graph(
            figure=fig,
            config={
                'displayModeBar': False,
                'responsive': True
            }
        )
    ], className='chart-container bg-white rounded-3 p-3 shadow-sm')


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
                            '대시보드'
                        ]),
                        href='/',
                        className='nav-link mx-3 hover-effect'
                    ),
                    dcc.Link(
                        html.Div([
                            html.I(className='fas fa-box me-2'),
                            '배송현황'
                        ]),
                        href='/delivery',
                        className='nav-link mx-3 hover-effect'
                    ),
                    dcc.Link(
                        html.Div([
                            html.I(className='fas fa-users me-2'),
                            '드라이버현황'
                        ]),
                        href='/driver',
                        className='nav-link mx-3 hover-effect'
                    ),
                ], className='navbar-nav ms-auto')
            ], className='container-fluid px-4')
        ]
    )
