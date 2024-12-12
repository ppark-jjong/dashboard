# delivery_page.py
from dash import html
from components import create_data_table
import data_generator as dg


def create_delivery_page():
    df = dg.generate_delivery_data()

    return html.Div([
        # 페이지 제목
        html.H2('배송 현황', className='mb-4'),

        # 데이터 테이블
        create_data_table(df, 'delivery')
    ])