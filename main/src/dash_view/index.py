from dash import Dash, html, page_container
import dash_bootstrap_components as dbc
from src.dash_view.pages import create_navbar
from flask import Flask

server = Flask(__name__)
app = Dash(
    __name__,
    server=server,
    use_pages=True,
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
        page_container,
        fluid=True,
        className="px-4"
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
