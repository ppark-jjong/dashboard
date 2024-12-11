# delivery_page.py
from dash import html, dash_table
import data_generator as dg


def create_delivery_page():
    df = dg.generate_delivery_data()

    return html.Div([
        html.H2('배송 현황', className='mb-4'),
        html.Button('새로고침', id='delivery-refresh', className='btn btn-primary mb-3'),
        dash_table.DataTable(
            id='delivery-table',
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i, "selectable": True} for i in df.columns],
            filter_action="native",  # 검색 기능 활성화
            page_action="native",  # 페이징 기능 활성화
            page_current=0,  # 현재 페이지
            page_size=15,  # 페이지당 로우 수
            sort_action="native",  # 정렬 기능 활성화
            sort_mode="multi",  # 다중 정렬 허용
            style_table={'overflowX': 'auto'},
            style_cell={
                'minWidth': '100px',
                'maxWidth': '300px',
                'whiteSpace': 'normal',
                'textAlign': 'center',
                'padding': '10px'
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'border': '1px solid #ddd'
            },
            style_data={
                'border': '1px solid #ddd'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                }
            ],
            style_filter={
                'backgroundColor': '#fff',
                'border': '1px solid #ddd'
            }
        )
    ])
