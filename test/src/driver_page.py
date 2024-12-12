# driver_page.py
from dash import html
from components import create_data_table
import data_generator as dg


def create_driver_page():
    df = dg.generate_driver_data()

    return html.Div([
        # 페이지 제목
        html.H2('드라이버 현황', className='mb-4'),

        # 데이터 테이블
        create_data_table(df, 'driver')
    ])