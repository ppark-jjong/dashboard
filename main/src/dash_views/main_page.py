from dash import html, dcc, callback
import plotly.express as px
from components import create_data_table, create_stats_card
import data_generator as dg


def create_status_chart(delivery_df):
    """배송 상태 파이 차트 생성"""
    status_counts = delivery_df['Status'].value_counts().reset_index()
    status_counts.columns = ['상태', '건수']

    # 상태별 색상 매핑 (success 카드와 동일한 초록색 사용)
    color_map = {
        '대기': '#B3D9FF',  # primary 카드 색상
        '배송중': '#FFE5B3',  # secondary 카드 색상
        '배송완료': '#B3FFB3'  # success 카드 색상
    }

    fig = px.pie(
        status_counts,
        values='건수',
        names='상태',
        title='배송 상태 분포',
        hole=0.4,
        color='상태',
        color_discrete_map=color_map
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
            'font': {'size': 16, 'color': '#2d3748'}
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

    return html.Div(
        className='chart-container bg-white rounded-3 p-3 shadow-sm',
        children=[
            dcc.Graph(
                figure=fig,
                config={'displayModeBar': False}
            )
        ]
    )


def create_department_chart(delivery_df):
    """부서별 배송 현황 파이 차트 생성"""
    dept_counts = delivery_df['Department'].value_counts().reset_index()
    dept_counts.columns = ['부서', '건수']

    # 부서별 파스텔톤 색상 사용
    colors = ['#FFB3B3', '#B3D9FF', '#FFE5B3', '#B3FFB3']

    fig = px.pie(
        dept_counts,
        values='건수',
        names='부서',
        title='부서별 배송 현황',
        hole=0.4,
        color_discrete_sequence=colors
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="부서: %{label}<br>건수: %{value}<br>비율: %{percent}<extra></extra>"
    )

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        title={
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.95,
            'yanchor': 'top',
            'font': {'size': 16, 'color': '#2d3748'}
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

    return html.Div(
        className='chart-container bg-white rounded-3 p-3 shadow-sm',
        children=[
            dcc.Graph(
                figure=fig,
                config={'displayModeBar': False}
            )
        ]
    )


def create_main_page():
    """메인 페이지 생성"""
    delivery_df = dg.generate_delivery_data()

    # 배송 상태별 통계
    waiting_count = len(delivery_df[delivery_df['Status'] == '대기'])
    in_progress_count = len(delivery_df[delivery_df['Status'] == '배송중'])
    completed_count = len(delivery_df[delivery_df['Status'] == '배송완료'])
    total_count = len(delivery_df)

    return html.Div([
        # 제목
        html.H2('배송 모니터링 대시보드', className='mb-4'),

        # 통계 카드 행
        html.Div([
            html.Div([
                create_stats_card(
                    '총 배송',
                    f"{total_count:,}건",
                    'fas fa-box',
                    'primary'  # 파스텔 빨간색
                )
            ], className='col-md-3'),
            html.Div([
                create_stats_card(
                    '배송 대기',
                    f"{waiting_count:,}건",
                    'fas fa-clock',
                    'secondary'  # 파스텔 파란색
                )
            ], className='col-md-3'),
            html.Div([
                create_stats_card(
                    '배송중',
                    f"{in_progress_count:,}건",
                    'fas fa-truck',
                    'warning'  # 파스텔 노란색
                )
            ], className='col-md-3'),
            html.Div([
                create_stats_card(
                    '배송 완료',
                    f"{completed_count:,}건",
                    'fas fa-check-circle',
                    'success'  # 파스텔 초록색
                )
            ], className='col-md-3')
        ], className='row g-3 mb-4'),

        # 차트 행
        html.Div([
            html.Div([
                create_status_chart(delivery_df)
            ], className='col-md-6'),
            html.Div([
                create_department_chart(delivery_df)
            ], className='col-md-6')
        ], className='row mb-4'),

        # 실시간 배송 현황 테이블
        html.Div([
            html.H3('긴급 배송 현황 (ETA 임박순)', className='h5 mb-3'),
            create_data_table(delivery_df.sort_values('ETA').head(5), 'main-delivery')
        ], className='mb-4'),

        # 실시간 업데이트 컴포넌트
        dcc.Interval(
            id='main-interval-component',
            interval=10 * 1000,  # 10초마다 업데이트
            n_intervals=0
        )
    ])