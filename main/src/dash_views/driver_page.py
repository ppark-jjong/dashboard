from dash import html, dash_table
import data_generator as dg


def create_driver_page():
    df = dg.generate_driver_data()

    return html.Div([
        html.H2('드라이버 현황', className='mb-4'),
        html.Button('새로고침', id='driver-refresh', className='btn btn-primary mb-3'),
        dash_table.DataTable(
            id='driver-table',
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i, "selectable": True} for i in df.columns],
            filter_action="native",
            page_action="native",
            page_current=0,
            page_size=15,
            sort_action="native",
            sort_mode="multi",
            style_table={'overflowX': 'auto'},
            style_cell={
                'minWidth': '100px',
                'maxWidth': '300px',
                'whiteSpace': 'normal',
                'textAlign': 'center',
                'padding': '10px'
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'border': '1px solid #ddd'
            },
            style_data={
                'border': '1px solid #ddd'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                }
            ],
            style_filter={
                'backgroundColor': '#fff',
                'border': '1px solid #ddd'
            }
        )
    ])