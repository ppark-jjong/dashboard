# main_page.py
from dash import html, dcc
import plotly.express as px
from components import create_data_table, create_stats_card
import data_generator as dg


def create_main_page():
    delivery_df = dg.generate_delivery_data()
    driver_df = dg.generate_driver_data()

    # 배송 상태별 통계
    waiting_count = len(delivery_df[delivery_df['Status'] == '대기'])
    in_progress_count = len(delivery_df[delivery_df['Status'] == '배송중'])
    completed_count = len(delivery_df[delivery_df['Status'] == '배송완료'])
    total_count = len(delivery_df)

    # 배송 상태 차트 데이터 준비
    delivery_status_counts = delivery_df['Status'].value_counts().reset_index()
    delivery_status_counts.columns = ['상태', '건수']  # 컬럼명 변경

    status_fig = px.pie(
        delivery_status_counts,
        values='건수',
        names='상태',
        title='배송 상태 분포',
        hole=0.4,
        color_discrete_sequence=['#FFB3B3', '#B3D9FF', '#FFE5B3', '#B3FFB3']  # 파스텔톤 색상
    )
    status_fig.update_traces(textposition='inside', textinfo='percent+label')
    status_fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        title_x=0.5,
        title_font_size=16
    )

    # 드라이버 상태 차트 데이터 준비
    driver_status_counts = driver_df['Status'].value_counts().reset_index()
    driver_status_counts.columns = ['상태', '건수']  # 컬럼명 변경

    driver_fig = px.pie(
        driver_status_counts,
        values='건수',
        names='상태',
        title='드라이버 상태 분포',
        hole=0.4,
        color_discrete_sequence=['#FFB3B3', '#B3D9FF', '#FFE5B3', '#B3FFB3']  # 파스텔톤 색상
    )
    driver_fig.update_traces(textposition='inside', textinfo='percent+label')
    driver_fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        title_x=0.5,
        title_font_size=16
    )

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
                dcc.Graph(figure=status_fig)
            ], className='col-md-6'),
            html.Div([
                dcc.Graph(figure=driver_fig)
            ], className='col-md-6')
        ], className='row mb-4'),

        # 실시간 데이터 테이블
        html.Div([
            html.H3('긴급 배송 현황 (ETA 임박순)', className='h5 mb-3'),
            create_data_table(
                delivery_df.sort_values('ETA').head(5),  # ETA 기준 정렬 후 상위 5개만 선택
                'main-delivery'
            )
        ], className='mb-4'),

        # 실시간 업데이트 컴포넌트
        dcc.Interval(
            id='main-interval-component',
            interval=10 * 1000,  # 10초마다 업데이트
            n_intervals=0
        )
    ])