# src/dash_view/index.py
from dash import Dash, html
import dash_bootstrap_components as dbc
from flask import Flask
from .main_navbar import create_navbar
from .dashboard import layout as dashboard_layout


def init_dash(server: Flask):
    """Dash 앱 초기화"""
    app = Dash(
        __name__,
        server=server,
        assets_folder="src/dash_view/assets",
        use_pages=False,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
        ],
        suppress_callback_exceptions=True,
        show_undo_redo=False
    )

    app._dev_tools.ui = False
    app.config.suppress_callback_exceptions = True
    app._suppress_callback_exceptions = True
    app.scripts.config.serve_locally = True

    navbar = create_navbar()

    app.layout = html.Div([
        navbar,
        dbc.Container(
            dashboard_layout(),  # 대시보드 페이지만 직접 렌더링
            fluid=True,
            className="px-4"
        )
    ])

    return app
