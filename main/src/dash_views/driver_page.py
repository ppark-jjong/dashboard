import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, callback, Output, Input, dash_table, dcc, State, callback_context
from .common import COLORS, status_color_map

def generate_sample_driver_data():
    data = [
        {
            '담당부서(Department)': 'Logistics',
            '기사명(Name)': '기사 1',
            '상태(Status)': '대기',
            '도착예정시간(ArriveTime)': '2024-12-10 15:00',
            '연락처(TelNumber)': '010-1111-2222'
        },
        {
            '담당부서(Department)': 'Express',
            '기사명(Name)': '기사 2',
            '상태(Status)': '배송중',
            '도착예정시간(ArriveTime)': '2024-12-10 16:30',
            '연락처(TelNumber)': '010-3333-4444'
        },
        {
            '담당부서(Department)': 'Special Delivery',
            '기사명(Name)': '기사 3',
            '상태(Status)': '복귀중',
            '도착예정시간(ArriveTime)': '2024-12-10 17:20',
            '연락처(TelNumber)': '010-5555-6666'
        },
        {
            '담당부서(Department)': 'Logistics',
            '기사명(Name)': '기사 4',
            '상태(Status)': '퇴근',
            '도착예정시간(ArriveTime)': '2024-12-10 18:00',
            '연락처(TelNumber)': '010-7777-8888'
        }
    ]
    data = data * 30
    df = pd.DataFrame(data)
    df.insert(0, 'No.', range(1, len(df)+1))
    return df

def create_status_cards(dataframe):
    status_counts = dataframe['상태(Status)'].value_counts()
    cards = []
    for status, count in status_counts.items():
        color = status_color_map.get(status, COLORS['text_primary'])
        cards.append(
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6(status, className="text-muted", style={
                            'fontSize':'1.1rem',
                            'color': COLORS['text_secondary'],
                            'textAlign':'center'
                        }),
                        html.H4(str(count), style={
                            'textAlign':'center',
                            'fontSize':'1.8rem',
                            'fontWeight':'bold',
                            'color': color
                        })
                    ], style={'padding':'1rem'})
                ], style={'border': f'1px solid {COLORS["bg_primary"]}', 'borderRadius':'5px'}),
                width=3
            )
        )
    return dbc.Row(cards, className="mb-3", style={'marginTop':'1rem', 'marginBottom':'1rem'})

card_style = {
    'padding': '1rem',
    'borderRadius': '8px',
    'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
    'backgroundColor': '#fff'
}

search_input_style = {
    'width': '200px',
    'borderRadius': '4px',
    'border': '1px solid #ccc',
    'padding': '0.5rem',
    'fontSize': '0.9rem'
}

driver_layout = [
    html.Div(style={'margin': '2rem 0'}),
    html.Div(id='driver-state-cards'),
    html.Div([
        dbc.Card([
            dbc.Row([
                dbc.Col([], width=3),
                dbc.Col(
                    html.Div(id='driver-pagination', style={'textAlign': 'center'}),
                    width=6
                ),
                dbc.Col(
                    html.Div(
                        dcc.Input(
                            id='driver-search-input',
                            type='text',
                            placeholder='검색...',
                            style=search_input_style
                        ),
                        style={'textAlign': 'right'}
                    ),
                    width=3
                )
            ], align='center', className="mb-3"),

            dash_table.DataTable(
                id='driver-table',
                columns=[],
                data=[],
                sort_action='custom',
                page_action='custom',
                page_current=0,
                page_size=15,
                style_cell={
                    'textAlign': 'center',
                    'fontSize': '1rem',
                    'padding': '0.5rem',
                    'border': '1px solid #ddd'
                },
                style_header={
                    'backgroundColor': '#f0f0f0',
                    'fontWeight': 'bold',
                    'border': '1px solid #ccc',
                    'borderBottom': '2px solid #ccc'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f9f9f9'
                    },
                    {
                        'if': {'state': 'active'},
                        'backgroundColor': '#e8f0fe',
                        'border': '1px solid #e8f0fe'
                    },
                    {
                        'if': {'column_id': 'No.'},
                        'backgroundColor': '#f7f7f7',
                        'fontWeight': 'bold',
                        'borderRight': '2px solid #ccc'
                    }
                ],
                style_table={'overflowX': 'auto', 'border': 'none'}
            ),
            dcc.Store(id='driver-total-rows')
        ], style=card_style)
    ], style={'marginTop': '2rem'})
]

@callback(
    Output('driver-table', 'data'),
    Output('driver-table', 'columns'),
    Output('driver-total-rows', 'data'),
    [Input('interval-component', 'n_intervals'),
     Input('driver-search-input', 'value'),
     Input('driver-table', 'page_current'),
     Input('driver-table', 'page_size'),
     Input('driver-table', 'sort_by')]
)
def update_driver_table(n, search_value, page_current, page_size, sort_by):
    df = generate_sample_driver_data()

    if search_value and search_value.strip():
        s = search_value.strip().lower()
        df = df[df.apply(lambda row: any(s in str(val).lower() for val in row), axis=1)]

    if sort_by and len(sort_by):
        df = df.sort_values(
            by=[col['column_id'] for col in sort_by],
            ascending=[col['direction'] == 'asc' for col in sort_by],
            inplace=False
        )

    columns = [{'name': c, 'id': c} for c in df.columns]
    total_rows = len(df)
    start = page_current * page_size
    end = start + page_size
    df_page = df.iloc[start:end]

    return df_page.to_dict('records'), columns, total_rows

@callback(
    Output('driver-pagination', 'children'),
    [Input('driver-total-rows', 'data'),
     Input('driver-table', 'page_current'),
     Input('driver-table', 'page_size')]
)
def update_driver_pagination(total_rows, page_current, page_size):
    if total_rows is None:
        return None
    total_pages = max(1, -(-total_rows // page_size))
    current_page = page_current + 1

    prev_disabled = current_page <= 1
    next_disabled = current_page >= total_pages

    return html.Div([
        dbc.Button("◀ 이전", id='driver-prev-page', disabled=prev_disabled, size='sm', color='secondary', className="me-2"),
        html.Span(f"페이지 {current_page} / {total_pages}", style={'fontSize': '0.9rem'}),
        dbc.Button("다음 ▶", id='driver-next-page', disabled=next_disabled, size='sm', color='secondary', className="ms-2")
    ], style={'display': 'inline-block'})

@callback(
    Output('driver-table', 'page_current'),
    [Input('driver-prev-page', 'n_clicks'),
     Input('driver-next-page', 'n_clicks')],
    [State('driver-table', 'page_current'),
     State('driver-total-rows', 'data'),
     State('driver-table', 'page_size')]
)
def paginate_driver(prev_clicks, next_clicks, page_current, total_rows, page_size):
    if total_rows is None:
        return page_current
    total_pages = max(1, -(-total_rows // page_size))

    ctx = callback_context
    if not ctx.triggered:
        return page_current

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'driver-prev-page' and page_current > 0:
        return page_current - 1
    elif trigger_id == 'driver-next-page' and page_current < total_pages - 1:
        return page_current + 1

    return page_current

@callback(
    Output('driver-state-cards', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_driver_state_cards(n):
    df = generate_sample_driver_data()
    return create_status_cards(df)
