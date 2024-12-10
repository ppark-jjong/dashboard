import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, callback, Output, Input, dash_table, dcc


def generate_sample_rider_data():
    data = [
        {
            'No.': 1,
            '담당부서': 'Logistics',
            '기사명': '김철수',
            '상태': '배송중',
            '도착예정시간': '2024-12-10 14:30',
            '연락처': '010-1234-5678',
            '총배송건수': 15,
            '완료건수': 10,
            '진행률': '66%'
        },
        {
            'No.': 2,
            '담당부서': 'Express',
            '기사명': '이영희',
            '상태': '대기',
            '도착예정시간': '2024-12-10 16:00',
            '연락처': '010-9876-5432',
            '총배송건수': 20,
            '완료건수': 5,
            '진행률': '25%'
        },
        {
            'No.': 3,
            '담당부서': 'Special Delivery',
            '기사명': '박영수',
            '상태': '완료',
            '도착예정시간': '2024-12-10 12:45',
            '연락처': '010-2222-3333',
            '총배송건수': 12,
            '완료건수': 12,
            '진행률': '100%'
        }
    ]
    data = data * 50
    df = pd.DataFrame(data)
    return df


# Styles
card_style = {
    'padding': '1.5rem',
    'borderRadius': '16px',
    'boxShadow': '0 10px 25px rgba(0,0,0,0.08)',
    'backgroundColor': 'white',
    'border': 'none',
    'margin': '1rem 0',
    'width': '100%'
}

search_input_style = {
    'width': '300px',
    'borderRadius': '8px',
    'border': '1px solid #e2e8f0',
    'padding': '0.5rem 1rem',
    'fontSize': '0.95rem',
    'marginBottom': '1rem'
}

rider_layout = [
    html.Div([
        dbc.Card([
            # Search Input
            html.Div([
                dcc.Input(
                    id='rider-search-input',
                    type='text',
                    placeholder='검색...',
                    style=search_input_style,
                    debounce=True
                )
            ], style={
                'display': 'flex',
                'justifyContent': 'flex-end',
                'width': '100%',
                'marginBottom': '1rem'
            }),

            dash_table.DataTable(
                id='rider-table',
                columns=[],
                data=[],
                sort_action='native',
                page_current=0,
                page_size=15,
                style_cell={
                    'textAlign': 'center',
                    'fontSize': '0.9rem',
                    'padding': '0.75rem',
                    'fontFamily': 'Arial, sans-serif',
                    'color': '#2c3e50',
                    'borderRight': '1px solid #e2e8f0'  # Add column separator
                },
                style_header={
                    'backgroundColor': '#f8fafc',
                    'fontWeight': '600',
                    'border': '1px solid #e2e8f0',
                    'borderBottom': '2px solid #3b82f6',
                    'textAlign': 'center',
                    'fontSize': '0.95rem',
                    'color': '#1e293b',
                    'textTransform': 'uppercase',
                    'cursor': 'pointer'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'},
                    {'if': {'state': 'active'}, 'backgroundColor': '#e9f3ff'},
                    {'if': {'column_id': 'No.'},
                     'backgroundColor': '#f1f5f9',
                     'fontWeight': 'bold'}
                ],
                style_table={
                    'overflowX': 'auto',
                    'border': 'none',
                    'borderRadius': '12px',
                    'width': '100%'
                },
                style_as_list_view=True
            ),

            # Pagination
            html.Div(id='rider-pagination', style={
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'marginTop': '1rem',
                'padding': '0.75rem',
                'backgroundColor': '#f8fafc',
                'borderRadius': '12px'
            })
        ], style=card_style)
    ], style={'width': '100%', 'padding': '1rem'})
]


@callback(
    Output('rider-table', 'data'),
    Output('rider-table', 'columns'),
    [Input('rider-search-input', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_rider_table(search_value, n):
    df = generate_sample_rider_data()

    # Search logic (search across all columns)
    if search_value and search_value.strip():
        s = search_value.strip().lower()
        df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(s).any(), axis=1)]

    columns = [{'name': col, 'id': col} for col in df.columns]
    page_size = 15
    df_page = df.head(page_size)

    return df_page.to_dict('records'), columns


@callback(
    Output('rider-pagination', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_rider_pagination(n):
    total_rows = len(generate_sample_rider_data())
    page_size = 15
    total_pages = max(1, -(-total_rows // page_size))

    return html.Div([
        dbc.Button("◀ 이전",
                   id='rider-prev-page',
                   size='sm',
                   color='primary',
                   className="me-3",
                   style={'borderRadius': '8px'}
                   ),
        html.Span(
            f"1 / {total_pages}",
            style={
                'fontSize': '0.9rem',
                'fontWeight': 'bold',
                'color': '#3b82f6',
                'margin': '0 1rem'
            }
        ),
        dbc.Button("다음 ▶",
                   id='rider-next-page',
                   size='sm',
                   color='primary',
                   className="ms-3",
                   style={'borderRadius': '8px'}
                   )
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center'
    })