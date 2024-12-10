import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, callback, Output, Input, dash_table, dcc, State, callback_context
from .common import create_stat_row


def generate_sample_delivery_data():
    data = [
        {
            '배송종류': '배송',
            '담당부서': 'Logistics',
            '배송유형': '방문수령',
            'DPS': 'DPS1234',
            '상태': '배송중',
            'ETA': '2024-12-10 14:30',
            '출발시간': '09:20',
            '주소': '10 Street, City',
            '수령인': '수령인 김철수',
            '연락처': '010-1234-5678'
        },
        {
            '배송종류': '회수',
            '담당부서': 'Express',
            '배송유형': '대리수령',
            'DPS': 'DPS5678',
            '상태': '대기',
            'ETA': '2024-12-10 16:00',
            '출발시간': '10:15',
            '주소': '22 Street, City',
            '수령인': '수령인 이영희',
            '연락처': '010-9876-5432'
        },
        {
            '배송종류': '배송',
            '담당부서': 'Special Delivery',
            '배송유형': '무인함',
            'DPS': 'DPS9999',
            '상태': '배송완료',
            'ETA': '2024-12-10 12:45',
            '출발시간': '08:30',
            '주소': '55 Street, City',
            '수령인': '수령인 박영수',
            '연락처': '010-2222-3333'
        }
    ]
    data = data * 50
    df = pd.DataFrame(data)
    df.insert(0, 'No.', range(1, len(df) + 1))
    return df


# Advanced Styling with Modern, Clean Design
card_style = {
    'padding': '1.5rem',
    'borderRadius': '16px',
    'boxShadow': '0 10px 25px rgba(0,0,0,0.1)',
    'backgroundColor': 'white',
    'border': 'none',
    'transition': 'all 0.3s ease'
}

top_container_style = {
    'display': 'flex',
    'justifyContent': 'space-between',
    'alignItems': 'center',
    'marginBottom': '1rem',
    'gap': '1rem'
}

search_input_style = {
    'width': '250px',
    'borderRadius': '8px',
    'border': '1px solid #ced4da',
    'padding': '0.5rem 1rem',
    'fontSize': '0.9rem',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
    'transition': 'all 0.3s ease'
}

pagination_style = {
    'display': 'flex',
    'justifyContent': 'center',
    'alignItems': 'center',
    'backgroundColor': '#f8f9fa',
    'borderRadius': '12px',
    'padding': '0.5rem',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
}

delivery_layout = [
    html.Div(style={'margin': '2rem 0'}),
    create_stat_row(50, 12, 38),
    html.Div([
        dbc.Card([
            # Top Container with Search and Pagination
            html.Div([
                dcc.Input(
                    id='global-search-input',
                    type='text',
                    placeholder='검색.',
                    style=search_input_style
                ),
                html.Div(id='table-top-pagination', style=pagination_style)
            ], style=top_container_style),

            dash_table.DataTable(
                id='delivery-table',
                columns=[],
                data=[],
                sort_action='native',
                sort_mode='multi',
                page_action='native',
                page_current=0,
                page_size=15,
                style_cell={
                    'textAlign': 'center',
                    'fontSize': '0.9rem',
                    'padding': '0.85rem',
                    'borderLeft': '1px solid #e9ecef',
                    'borderRight': '1px solid #e9ecef',
                    'border': '1px solid #dee2e6'  # 셀 구분선 추가
                },
                style_header={
                    'backgroundColor': '#f1f3f5',
                    'fontWeight': 'bold',
                    'border': '2px solid #339af0',
                    'textAlign': 'center',
                    'fontSize': '0.95rem',
                    'cursor': 'pointer'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8f9fa'
                    },
                    {
                        'if': {'state': 'active'},
                        'backgroundColor': '#e7f5ff',
                        'border': '1px solid #339af0'
                    },
                    {
                        'if': {'column_id': 'No.'},
                        'backgroundColor': '#f1f3f5',
                        'fontWeight': 'bold'
                    }
                ],
                style_table={
                    'overflowX': 'auto',
                    'border': '1px solid #dee2e6',
                    'borderRadius': '12px'
                }
            ),

            # Bottom Pagination
            html.Div(id='table-bottom-pagination', style=pagination_style)
        ], style=card_style)
    ], style={'marginTop': '2rem'})
]


@callback(
    Output('delivery-table', 'data'),
    Output('delivery-table', 'columns'),
    Output('table-top-pagination', 'children'),
    Output('table-bottom-pagination', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input('global-search-input', 'value'),
     Input('delivery-table', 'page_current')]
)
def update_delivery_table(n, search_value, page_current):
    df = generate_sample_delivery_data()

    # 글로벌 검색
    if search_value and search_value.strip():
        s = search_value.strip().lower()
        df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(s).any(), axis=1)]

    columns = [{'name': col, 'id': col} for col in df.columns]
    total_pages = max(1, -(-len(df) // 15))
    current_page = page_current + 1

    # 페이지네이션 버튼 생성
    pagination = html.Div([
        dbc.Button("◀ 이전",
                   id='top-prev-page',
                   disabled=current_page <= 1,
                   size='sm',
                   color='primary',
                   className="me-2",
                   style={'borderRadius': '6px'}
                   ),
        html.Span(
            f"페이지 {current_page} / {total_pages}",
            style={
                'fontSize': '0.9rem',
                'fontWeight': 'bold',
                'color': '#339af0',
                'margin': '0 0.5rem'
            }
        ),
        dbc.Button("다음 ▶",
                   id='top-next-page',
                   disabled=current_page >= total_pages,
                   size='sm',
                   color='primary',
                   className="ms-2",
                   style={'borderRadius': '6px'}
                   )
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center'
    })

    # 페이지 데이터 슬라이싱
    start = page_current * 15
    end = start + 15
    page_data = df.iloc[start:end]

    return page_data.to_dict('records'), columns, pagination, pagination


@callback(
    Output('delivery-table', 'page_current'),
    [Input('top-prev-page', 'n_clicks'),
     Input('top-next-page', 'n_clicks')],
    [State('delivery-table', 'page_current'),
     State('delivery-table', 'data')]
)
def update_page(prev_clicks, next_clicks, current_page, data):
    ctx = callback_context
    if not ctx.triggered:
        return current_page

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'top-prev-page' and current_page > 0:
        return current_page - 1
    elif trigger_id == 'top-next-page':
        return current_page + 1

    return current_page