# components.py
from dash import html, dcc, dash_table
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_stats_card(title, value, icon, color):
    """
    엔터프라이즈 통계 카드 컴포넌트
    """
    return html.Div(
        className='card shadow-sm h-100',
        children=[
            html.Div(
                className=f'card-body d-flex align-items-center border-start border-5 border-{color}',
                children=[
                    html.I(className=f'{icon} fs-1 text-{color} me-3'),
                    html.Div([
                        html.H6(title, className='card-subtitle text-muted'),
                        html.H4(value, className='card-title mb-0 fw-bold')
                    ])
                ]
            )
        ]
    )

    def create_navbar():
        """
        모던 네비게이션 바 컴포넌트
        """
        return html.Nav(
            className='navbar navbar-expand-lg navbar-light bg-white shadow-sm',
            children=[
                html.Div([
                    html.Span('🚚 Smart Delivery', className='navbar-brand fw-bold'),
                    html.Div([
                        dcc.Link('대시보드', href='/', className='nav-link mx-3'),
                        dcc.Link('배송현황', href='/delivery', className='nav-link mx-3'),
                        dcc.Link('드라이버현황', href='/driver', className='nav-link mx-3'),
                    ], className='navbar-nav ms-auto')
                ], className='container')
            ]
        )

    def create_refresh_button(id_prefix):
        """
        새로고침 버튼 컴포넌트
        """
        return html.Button(
            children=[
                html.I(className='fas fa-sync-alt me-2'),
                '새로고침'
            ],
            id=f'{id_prefix}-refresh',
            className='btn btn-primary mb-4'
        )

    def create_data_table(df, id_prefix):
        """
        엔터프라이즈급 데이터 테이블 컴포넌트

        Args:
            df (pd.DataFrame): 표시할 데이터프레임
            id_prefix (str): 테이블 컴포넌트의 고유 식별자
        """
        # 컬럼별 스타일 정의
        status_style = {
            'if': {'column_id': 'Status'},
            'minWidth': '100px',
            'width': '100px',
            'maxWidth': '100px',
            'textAlign': 'center'
        }

        time_columns = ['DepartTime', 'ArrivalTime', 'ETA']
        time_styles = [
            {
                'if': {'column_id': col},
                'minWidth': '120px',
                'width': '120px',
                'maxWidth': '120px',
                'textAlign': 'center'
            } for col in time_columns
        ]

        address_style = {
            'if': {'column_id': 'Address'},
            'minWidth': '300px',
            'width': '300px',
            'maxWidth': '300px'
        }

        # 모든 스타일 결합
        conditional_styles = [status_style] + time_styles + [address_style]

        return html.Div([
            # 테이블 컨트롤
            html.Div([
                html.Button(
                    children=[
                        html.I(className='fas fa-sync-alt me-2'),
                        '새로고침'
                    ],
                    id=f'{id_prefix}-refresh',
                    className='btn btn-primary mb-3'
                ),
            ], className='d-flex justify-content-between align-items-center'),

            # 데이터 테이블
            dash_table.DataTable(
                id=f'{id_prefix}-table',
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],

                # 페이지네이션 설정
                page_action='native',
                page_current=0,
                page_size=15,

                # 정렬 설정
                sort_action='native',
                sort_mode='multi',

                # 테이블 스타일링
                style_table={
                    'overflowX': 'auto',
                    'borderRadius': '8px',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.1)',
                    'border': '1px solid #eee',
                    'backgroundColor': 'white'
                },

                # 헤더 스타일링
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'color': '#2c3e50',
                    'fontWeight': '600',
                    'textAlign': 'center',
                    'padding': '15px',
                    'borderBottom': '2px solid #dee2e6',
                    'borderTop': 'none',
                    'borderLeft': 'none',
                    'borderRight': 'none',
                    'fontSize': '14px'
                },

                # 셀 스타일링
                style_cell={
                    'textAlign': 'left',
                    'padding': '15px',
                    'fontFamily': 'Noto Sans KR, sans-serif',
                    'fontSize': '14px',
                    'color': '#2c3e50',
                    'borderBottom': '1px solid #eee',
                    'borderLeft': 'none',
                    'borderRight': 'none'
                },

                # 데이터 행 스타일링
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '1.5'
                },

                # 조건부 스타일링
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8f9fa'
                    },
                    {
                        'if': {'row_index': 'even'},
                        'backgroundColor': 'white'
                    }
                ],

                # 컬럼별 스타일링 적용
                style_cell_conditional=conditional_styles
            )
        ], className='table-container shadow-sm')