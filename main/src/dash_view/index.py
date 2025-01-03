# src/dash_view/index.py
from dash import Dash, html
import dash_bootstrap_components as dbc
from flask import Flask
from .main_navbar import create_navbar
from .dashboard import layout as dashboard_layout
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_dash(server: Flask):
    """Dash 앱 초기화"""
    # assets 폴더 경로 설정
    assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    logger.info(f"Assets 폴더 경로: {assets_path}")

    # assets 폴더 확인 및 생성
    if not os.path.exists(assets_path):
        logger.info(f"Assets 폴더가 없습니다. 새로 생성합니다: {assets_path}")
        os.makedirs(assets_path)
    else:
        logger.info("Assets 폴더가 이미 존재합니다.")

    # CSS 파일 경로
    css_file = os.path.join(assets_path, 'styles.css')

    # CSS 파일 확인 및 생성
    if not os.path.exists(css_file):
        logger.info(f"기본 CSS 파일이 없습니다. 새로 생성합니다: {css_file}")
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write("""
/* 기본 스타일 */
body {
    font-family: Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    background-color: #f8f9fa;
}

/* 버튼 스타일 */
.btn {
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    transition: all 0.2s ease-in-out;
}

/* 테이블 스타일 */
.dash-table {
    border-radius: 8px;
    overflow: hidden;
}
            """)
        logger.info("기본 CSS 파일이 생성되었습니다.")
    else:
        logger.info("CSS 파일이 이미 존재합니다.")

    # Dash 앱 초기화
    logger.info("Dash 앱 초기화를 시작합니다.")
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/api/dashboard/',
        assets_folder=assets_path,
        use_pages=False,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
        ],
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
        suppress_callback_exceptions=True,
        show_undo_redo=False
    )

    # 앱 설정
    app._dev_tools.ui = False
    app.config.suppress_callback_exceptions = True
    app._suppress_callback_exceptions = True
    app.scripts.config.serve_locally = True

    logger.info("Dash 앱 초기화가 완료되었습니다.")

    # 네비게이션 바 생성
    navbar = create_navbar()

    # 레이아웃 설정
    app.layout = html.Div([
        navbar,
        dbc.Container(
            dashboard_layout(),
            fluid=True,
            className="px-4"
        )
    ])

    logger.info("Dash 앱 레이아웃이 설정되었습니다.")
    return app