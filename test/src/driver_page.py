import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, callback, Output, Input, dash_table, dcc, State, callback_context
from common import create_stat_row

def generate_sample_driver_data():
    data = [
        {
            'No.': idx + 1,
            '담당부서': 'Logistics',
            '기사명': f'기사 {idx + 1}',
            '상태': ['대기', '배송중', '복귀중', '퇴근'][idx % 4],
            '도착예정시간': f'2024-12-10 {8 + idx % 9}:00',
            '연락처': f'010-{1000 + idx % 9000:04d}'
        }
        for idx in range(50)
    ]
    return pd.DataFrame(data)

driver_layout = [
    html.Div(style={'margin': '2rem 0'}),
    create_stat_row(50, 20, 30),
    dbc.Card([
        html.Div([
            dcc.Input(
                id='driver-search-input',
                type='text',
                placeholder='검색...',
                style={
                    'width': '250px',
                    'marginRight': '10px',
                    'padding': '0.5rem',
                    'borderRadius': '5px',
                    'border': '1px solid #ccc'
                }
            ),
            dbc.Button("검색", id='driver-search-button', color="primary")
        ], style={'display': 'flex', 'justifyContent': 'flex-end', 'marginBottom': '1rem'}),
        dash_table.DataTable(
            id='driver-table',
            columns=[],
            data=[],
            sort_action='native',
            style_cell={
                'textAlign': 'center',
                'fontSize': '0.9rem',
                'padding': '0.85rem'
            },
            style_header={
                'fontWeight': 'bold',
                'fontSize': '0.95rem',
            },
            style_data_conditional=[
                {'if': {'column_id': 'No.'}, 'width': '50px', 'textAlign': 'center', 'pointerEvents': 'none'}
            ]
        )
    ], style={'padding': '1rem', 'borderRadius': '12px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'})
]

@callback(
    Output('driver-table', 'data'),
    Output('driver-table', 'columns'),
    [Input('driver-search-button', 'n_clicks')],
    [State('driver-search-input', 'value')]
)
def update_driver_table(n_clicks, search_value):
    df = generate_sample_driver_data()

    if search_value:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_value, case=False).any(), axis=1)]

    columns = [{'name': col, 'id': col} for col in df.columns]
    return df.to_dict('records'), columns
