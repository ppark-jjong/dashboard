from dash import html, dash_table
import dash_bootstrap_components as dbc
from src.dash_views.data_generate import DataGenerator
from src.dash_views.components import DashComponents
from src.dash_views.styles import StyleManager


def create_delivery_layout():
    df = DataGenerator.generate_delivery_data()
    columns = DataGenerator.get_column_definitions()['delivery']['columns']
    styles = StyleManager.get_common_styles()

    return html.Div([
        dbc.Container([
            dbc.Card([
                dbc.CardBody([
                    # 검색 및 새로고침 섹션
                    DashComponents.create_search_refresh_section(
                        'delivery-search-input',
                        'delivery-refresh-button'
                    ),
                    # 데이터 테이블
                    dash_table.DataTable(
                        id='delivery-table',
                        columns=columns,
                        data=df.to_dict('records'),
                        page_size=10,
                        style_table=styles['table']['cell'],
                        style_cell=styles['table']['cell'],
                        style_header=styles['table']['header'],
                        page_action='native',
                        sort_action='native',
                        filter_action='native',
                        style_data_conditional=[{
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }]
                    )
                ])
            ], style=styles['card'])
        ], fluid=True)
    ], style=styles['container'])