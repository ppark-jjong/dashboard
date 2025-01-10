# src/dash_view/index.py
from dash import Dash, html
import dash_bootstrap_components as dbc
from flask import Flask
from .main_navbar import create_navbar
from .dashboard import layout as dashboard_layout
from .callbacks import dashboard_callbacks
import os
import logging

logger = logging.getLogger(__name__)

def init_dash(server: Flask):
    logger.info("Initializing Dash app...")
    try:
        # callbacks 임포트 확인
        logger.info("Loading dashboard callbacks...")
        logger.info("Dashboard callbacks successfully loaded")
    except Exception as e:
        logger.error(f"Failed to import dashboard callbacks: {e}")
        raise

    assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/api/dashboard/',
        assets_folder=assets_path,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
        ],
        suppress_callback_exceptions=True
    )

    app.layout = html.Div([
        create_navbar(),
        dbc.Container(
            dashboard_layout(),
            fluid=True,
            className="dashboard-container"
        )
    ], className="app-wrapper")

    logger.info("Dash app initialization completed")
    return app