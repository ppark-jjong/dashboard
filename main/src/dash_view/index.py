# index.py
from dash import Dash, html, dcc, page_container
import dash_bootstrap_components as dbc
from flask import Flask

server = Flask(__name__)
app = Dash(
    __name__,
    server=server,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap'
    ],
    suppress_callback_exceptions=True,  # 콜백 예외 억제
    show_undo_redo=False  # 실행 취소/다시 실행 버튼 숨기기
)
app.config.suppress_callback_exceptions = True
app._suppress_callback_exceptions = True
app.scripts.config.serve_locally = True
# 네비게이션 바
navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(dbc.NavbarBrand("Delivery Dashboard", className="ms-2")),
            ],
                align="center",
                className="g-0",
            ),
            href="/",
            style={"textDecoration": "none"},
        ),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Main", href="/")),
            dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
            dbc.NavItem(dbc.NavLink("KPI", href="/kpi")),
        ],
            className="ms-auto")
    ]),
    color="light",
    className="mb-4 shadow-sm"
)

app.layout = html.Div([
    navbar,
    dbc.Container(
        page_container,
        fluid=True,
        className="px-4"
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
