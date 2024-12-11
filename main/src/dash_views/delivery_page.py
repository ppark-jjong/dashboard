
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from src.dash_views.components import DashComponents
from src.dash_views.layouts import LayoutManager
from src.dash_views.data_generate import DataGenerator


def create_delivery_layout():
    """
    배송 현황 페이지 레이아웃 생성 - 최적화된 버전

    Returns:
        html.Div: 직렬화 가능한 Dash 컴포넌트 트리
    """
    try:
        # 데이터 준비
        df = DataGenerator.generate_delivery_data()
        columns = DataGenerator.get_column_definitions()['delivery']['columns']

        # 검색 및 새로고침 섹션 스타일
        search_section_style = {
            'display': 'flex',
            'alignItems': 'center',
            'gap': '12px',
            'marginBottom': '20px',
            'padding': '15px'
        }

        # 버튼 스타일
        button_style = {
            'backgroundColor': '#3b82f6',
            'color': 'white',
            'border': 'none',
            'borderRadius': '8px',
            'padding': '10px 20px',
            'fontSize': '14px'
        }

        # 검색 입력 스타일
        input_style = {
            'width': '300px',
            'padding': '10px',
            'borderRadius': '8px',
            'border': '1px solid #e2e8f0'
        }

        # 테이블 스타일
        table_style = {
            'overflowX': 'auto',
            'marginTop': '20px'
        }

        return html.Div([
            # 검색 및 필터 섹션
            html.Div([
                dbc.Button(
                    "새로고침",
                    id='delivery-refresh-button',
                    color='primary',
                    style=button_style,
                    className='me-3'
                ),
                dbc.Input(
                    id='delivery-search-input',
                    type='text',
                    placeholder='검색어를 입력하세요',
                    style=input_style
                )
            ], style=search_section_style),

            # 데이터 테이블
            html.Div([
                dash_table.DataTable(
                    id='delivery-table',
                    columns=columns,
                    data=df.to_dict('records'),
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'whiteSpace': 'normal'
                    },
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold',
                        'border': '1px solid #dee2e6'
                    },
                    page_size=10,
                    sort_action='native',
                    filter_action='native'
                )
            ], style=table_style)
        ])

    except Exception as e:
        logging.error(f"배송 현황 페이지 생성 오류: {str(e)}")
        return html.Div("데이터 로딩 중 오류가 발생했습니다.", className="alert alert-danger")