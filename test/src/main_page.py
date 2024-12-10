import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from common import create_pie_chart
from driver_page import driver_layout
from delivery_page import delivery_layout

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("배송 관리 시스템", className="text-center", style={'marginTop': '20px'}), width=12)
    ]),
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label="기사 현황", children=driver_layout),
        dcc.Tab(label="배송 현황", children=delivery_layout)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("새로고침", id='refresh-button', color="primary", className="me-2", style={'float': 'right'}),
            dcc.Interval(id='interval-component', interval=10000, n_intervals=0)
        ], width=12)
    ])
], fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True)
