# app.py

import dash
from dash import html, dcc, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import logging
from typing import Optional, Dict, Any

from src.dash_views.main_page import create_main_dashboard
from src.dash_views.delivery_page import create_delivery_layout
from src.dash_views.driver_page import create_driver_layout
from src.dash_views.layouts import LayoutManager


class DashboardApp:
    """대시보드 애플리케이션 핵심 클래스"""

    def __init__(self):
        """애플리케이션 초기화 및 기본 설정"""
        self.app = Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )
        self._init_layout()
        self._register_callbacks()

    def _init_layout(self):
        """기본 레이아웃 구성"""
        self.app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='navbar'),
            html.Div(id='page-content')
        ])

    def _register_callbacks(self):
        @self.app.callback(
            [Output('page-content', 'children'),
             Output('navbar', 'children')],
            [Input('url', 'pathname')]
        )
        def update_page(pathname: str) -> tuple:
            """
            페이지 업데이트 콜백 - 직렬화 보장
            """
            try:
                if pathname is None:
                    pathname = '/'

                # 페이지 컴포넌트 생성
                page_content = self._get_page_content(pathname)
                navbar = LayoutManager.create_navbar(pathname)

                # 직렬화 가능성 검증
                if not isinstance(page_content, (html.Div, dict, str)):
                    raise ValueError("유효하지 않은 페이지 컴포넌트")

                return page_content, navbar

            except Exception as e:
                logging.error(f"페이지 업데이트 오류: {str(e)}")
                return html.Div("오류가 발생했습니다"), LayoutManager.create_navbar('/')

    def run(self, host: str = "0.0.0.0", port: int = 8050, debug: bool = True):
        """서버 실행"""
        self.app.run_server(host=host, port=port, debug=debug)


def main():
    """애플리케이션 실행 엔트리포인트"""
    try:
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(module)s - %(message)s'
        )

        # 애플리케이션 실행
        logging.info("대시보드 서버 시작")
        app = DashboardApp()
        app.run()

    except Exception as e:
        logging.error(f"서버 실행 오류: {str(e)}")
        raise


if __name__ == '__main__':
    main()
