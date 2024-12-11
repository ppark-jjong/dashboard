# driver_page.py
from dash import html, callback, Output, Input
from .components import DashComponents
from .layouts import LayoutManager
from .data_generate import DataGenerator


def create_driver_layout():
    """기사 현황 페이지 레이아웃 생성"""
    df = DataGenerator.generate_rider_data()
    columns = DataGenerator.get_column_definitions()['rider']['columns']

    content = html.Div([
        # 기존 설정값을 직접 전달하는 방식으로 변경
        DashComponents.create_search_refresh_section(
            'rider-search-input',
            'rider-refresh-button'
        ),
        DashComponents.create_data_table(
            table_id='rider-table',
            columns=columns,
            data=df.to_dict('records')
        )
    ])

    return LayoutManager.create_page_layout(content)