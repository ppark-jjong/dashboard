# main_page.py
from dash import html, dcc, dash_table
import plotly.express as px
from data_generator import generate_delivery_data, generate_driver_data


def create_main_page():
    delivery_df = generate_delivery_data()
    driver_df = generate_driver_data()

    # 실시간 배송 현황
    delivery_status = delivery_df['Status'].value_counts()
    status_fig = px.pie(
        values=delivery_status.values,
        names=delivery_status.index,
        title='실시간 배송 현황',
        hole=0.4,
        color_discrete_sequence=['#4CAF50', '#2196F3', '#FFC107']
    )
    status_fig.update_traces(textposition='inside', textinfo='percent+label')

    # 실시간 드라이버 현황
    driver_status = driver_df['Status'].value_counts()
    driver_fig = px.pie(
        values=driver_status.values,
        names=driver_status.index,
        title='실시간 드라이버 현황',
        hole=0.4,
        color_discrete_sequence=['#FF5722', '#9C27B0', '#3F51B5', '#607D8B']
    )
    driver_fig.update_traces(textposition='inside', textinfo='percent+label')

    return html.Div([
        # 실시간 통계 카드
        html.Div([
            html.Div([
                html.Div([
                    html.H3(f"{len(delivery_df):,}건", className='display-4 fw-bold text-primary'),
                    html.P("총 배송", className='lead')
                ], className='bg-white p-4 rounded-3 shadow-sm text-center')
            ], className='col-md-4'),
            html.Div([
                html.Div([
                    html.H3(f"{len(driver_df):,}명", className='display-4 fw-bold text-success'),
                    html.P("총 드라이버", className='lead')
                ], className='bg-white p-4 rounded-3 shadow-sm text-center')
            ], className='col-md-4'),
            html.Div([
                html.Div([
                    html.H3(f"{driver_df['Qty'].sum():,}건", className='display-4 fw-bold text-info'),
                    html.P("총 처리량", className='lead')
                ], className='bg-white p-4 rounded-3 shadow-sm text-center')
            ], className='col-md-4'),
        ], className='row mb-4'),

        # 실시간 차트
        html.Div([
            html.Div([
                dcc.Graph(figure=status_fig)
            ], className='col-md-6'),
            html.Div([
                dcc.Graph(figure=driver_fig)
            ], className='col-md-6')
        ], className='row mb-4'),

        # 실시간 업데이트 컴포넌트
        dcc.Interval(
            id='main-interval-component',
            interval=10 * 1000,  # 10초마다 업데이트
            n_intervals=0
        )
    ])