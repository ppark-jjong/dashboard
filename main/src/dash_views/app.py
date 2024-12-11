# app.py
from dash import Dash, html, dcc, dash
from dash.dependencies import Input, Output
import delivery_page
import driver_page
import main_page
import data_generator as dg

app = Dash(__name__,
    external_stylesheets=[
        'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'
    ]
)

app.layout = html.Div([
    html.Nav(
        className='navbar navbar-expand-lg navbar-dark bg-primary mb-4',
        children=[
            html.Div([
                html.Span('배송 모니터링 시스템', className='navbar-brand'),
                html.Div([
                    dcc.Link('대시보드', href='/', className='nav-link text-white'),
                    dcc.Link('배송현황', href='/delivery', className='nav-link text-white'),
                    dcc.Link('드라이버현황', href='/driver', className='nav-link text-white'),
                ], className='navbar-nav')
            ], className='container')
        ]
    ),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', className='container')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/delivery':
        return delivery_page.create_delivery_page()
    elif pathname == '/driver':
        return driver_page.create_driver_page()
    return main_page.create_main_page()

@app.callback(
    Output('delivery-table', 'data'),
    Input('delivery-refresh', 'n_clicks')
)
def refresh_delivery_data(n_clicks):
    if n_clicks is None:
        return dash.no_update
    return dg.generate_delivery_data().to_dict('records')

@app.callback(
    Output('driver-table', 'data'),
    Input('driver-refresh', 'n_clicks')
)
def refresh_driver_data(n_clicks):
    if n_clicks is None:
        return dash.no_update
    return dg.generate_driver_data().to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)