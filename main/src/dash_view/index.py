# src/dash_view/index.py
from dash import Dash
import dash_bootstrap_components as dbc
from flask import Flask
from .dashboard import layout as dashboard_layout
from .main_navbar import create_navbar
from .callbacks import dashboard_callbacks
import os
import logging
from dash import html

logger = logging.getLogger(__name__)

def create_layout():
    """전체 앱 레이아웃 생성"""
    return html.Div([
        create_navbar(),  # Navbar 추가
        dashboard_layout()  # Dashboard 레이아웃 추가
    ])

def init_dash(server: Flask) -> Dash:
    """Dash 앱 초기화"""
    try:
        assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

        app = Dash(
            __name__,
            server=server,
            url_base_pathname='/',
            assets_folder=assets_path,
            external_stylesheets=[
                dbc.themes.BOOTSTRAP,
                'https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
            ],
            suppress_callback_exceptions=True
        )

        # 전체 레이아웃 설정
        app.layout = create_layout()

        # 콜백 초기화
        dashboard_callbacks.init_callbacks(app)

        return app

    except Exception as e:
        logger.error(f"Failed to initialize Dash app: {e}")
        raise