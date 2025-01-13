# src/dash_view/index.py
from dash import Dash, html
import dash_bootstrap_components as dbc
from flask import Flask
from .main_navbar import create_navbar
from .dashboard import layout as dashboard_layout
from .callbacks import *  # 콜백 함수들 임포트
import os
import logging

logger = logging.getLogger(__name__)


def init_dash(server: Flask) -> Dash:
    """Dash 앱 초기화"""
    logger.info("Initializing Dash app...")

    try:
        # 애셋 경로 설정
        assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        logger.info(f"Assets path: {assets_path}")

        # Dash 앱 생성
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

        # 레이아웃 설정
        app.layout = html.Div([
            create_navbar(),
            dbc.Container(
                dashboard_layout(),
                fluid=True,
                className="dashboard-container py-4"
            )
        ], className="app-wrapper")

        logger.info("Dash app initialized successfully")
        return app

    except Exception as e:
        logger.error(f"Failed to initialize Dash app: {e}")
        raise