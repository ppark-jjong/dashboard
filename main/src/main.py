import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, callback, Output, Input, dash_table, dcc


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
    return pd.DataFrame(data)


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

# 새로운 스타일 정의
refresh_button_style = {
    'backgroundColor': '#f0f9ff',  # 연한 파란 배경
    'border': '1px solid #3b82f6',  # 파란 테두리
    'borderRadius': '8px',
    'padding': '0.5rem 1rem',
    'fontSize': '0.9rem',
    'marginRight': '0.75rem',
    'cursor': 'pointer',
    'color': '#3b82f6',  # 버튼 텍스트 색상
    'fontWeight': '600',
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center',
    'transition': 'all 0.3s ease',
    'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'
}

refresh_button_hover_style = {
    ':hover': {
        'backgroundColor': '#3b82f6',
        'color': 'white',
        'boxShadow': '0 6px 8px rgba(0,0,0,0.1)'
    }
}

pagination_container_style = {
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center',
    'gap': '0.5rem',
    'padding': '1rem',
    'backgroundColor': '#f8fafc',
    'borderRadius': '12px',
    'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'
}

pagination_button_style = {
    'height': '40px',
    'minWidth': '40px',
    'padding': '0 0.75rem',
    'fontSize': '0.875rem',
    'backgroundColor': 'white',
    'border': '1px solid #e2e8f0',
    'color': '#64748b',
    'cursor': 'pointer',
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center',
    'borderRadius': '6px',
    'transition': 'all 0.3s ease',
    'fontWeight': '500',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.04)'
}

pagination_button_hover_style = {
    ':hover': {
        'backgroundColor': '#f1f5f9',
        'borderColor': '#3b82f6',
        'color': '#3b82f6',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.08)'
    }
}

current_page_style = {
    'backgroundColor': '#3b82f6',
    'color': 'white',
    'fontWeight': '700',
    'border': 'none',
    'boxShadow': '0 4px 6px rgba(59,130,246,0.3)'
}
# Initialize with sample data
initial_df = generate_sample_delivery_data()
initial_columns = [
    {
        'name': col,
        'id': col,
        'type': 'numeric' if initial_df[col].dtype in ['int64', 'float64'] else 'text'
    } for col in initial_df.columns
]

delivery_layout = [
    html.Div([
        dbc.Card([
            # 새로고침 및 검색 컨테이너
            html.Div([
                # 새로고침 버튼
                html.Button(
                    "새로고침",
                    id='delivery-refresh-button',
                    style={**refresh_button_style, **refresh_button_hover_style}
                ),

                # 검색 입력
                dcc.Input(
                    id='delivery-search-input',
                    type='text',
                    placeholder='검색...',
                    style=search_input_style,
                    debounce=True
                )
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'width': '100%',
                'marginBottom': '1rem'
            }),

            dash_table.DataTable(
                id='delivery-table',
                columns=initial_columns,
                data=initial_df.head(15).to_dict('records'),
                sort_action='native',
                sort_mode='multi',
                page_current=0,
                page_size=15,
                style_cell={
                    'textAlign': 'center',
                    'fontSize': '0.9rem',
                    'padding': '0.75rem',
                    'fontFamily': 'Arial, sans-serif',
                    'color': '#2c3e50',
                    'borderRight': '1px solid #e2e8f0',
                    'borderLeft': '1px solid #e2e8f0',
                    'minWidth': '120px',
                    'width': '150px',
                    'maxWidth': '300px'
                },
                style_header={
                    'backgroundColor': '#f8fafc',
                    'fontWeight': '600',
                    'border': '1px solid #e2e8f0',
                    'borderBottom': '2px solid #3b82f6',
                    'textAlign': 'center',
                    'fontSize': '0.95rem',
                    'color': '#1e293b',
                    'height': '56px',
                    'cursor': 'pointer',
                    'padding': '0 1rem',
                    'position': 'relative'
                },
                style_header_conditional=[{
                    'if': {'column_id': col},
                    'textDecoration': 'none',
                    ':hover': {
                        'backgroundColor': '#f1f5f9',
                        'color': '#0f172a'
                    }
                } for col in initial_df.columns],
                sort_as_null=['', 'None', 'null', 'NaN'],
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'},
                    {'if': {'state': 'active'}, 'backgroundColor': '#e9f3ff'},
                    {'if': {'state': 'selected'}, 'backgroundColor': '#e9f3ff', 'border': '1px solid #3b82f6'}
                ],
                style_table={
                    'overflowX': 'auto',
                    'border': 'none',
                    'borderRadius': '12px',
                    'width': '100%'
                }
            ),

            # 페이지네이션
            html.Div(id='delivery-pagination', style=pagination_container_style)
        ], style=card_style)
    ], style={'width': '100%', 'padding': '1rem'})
]
@callback(
    [Output('delivery-table', 'data'),
     Output('delivery-table', 'page_current')],
    [Input('delivery-search-input', 'value'),
     Input('delivery-refresh-button', 'n_clicks')]
)
def update_table_and_refresh(search_value, n_clicks):
    df = generate_sample_delivery_data()

    # Handle search
    if search_value and search_value.strip():
        s = search_value.strip().lower()
        df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(s).any(), axis=1)]

    # Always return to first page when refreshing or searching
    return df.head(15).to_dict('records'), 0


@callback(
    [Output('delivery-table', 'data'),
     Output('delivery-table', 'page_current')],
    [Input('delivery-search-input', 'value'),
     Input('delivery-refresh-button', 'n_clicks')]
)
def update_table_and_refresh(search_value, n_clicks):
    df = generate_sample_delivery_data()

    if search_value and search_value.strip():
        s = search_value.strip().lower()
        df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(s).any(), axis=1)]

    return df.head(15).to_dict('records'), 0


@callback(
    Output('delivery-pagination', 'children'),
    [Input('delivery-table', 'page_current')]
)
def update_pagination(current_page):
    if current_page is None:
        current_page = 0

    total_rows = len(generate_sample_delivery_data())
    page_size = 15
    total_pages = max(1, -(-total_rows // page_size))
    current_page = current_page + 1  # 1-based 인덱스로 변환

    # 보여줄 페이지 번호 계산
    visible_pages = 5
    half_visible = visible_pages // 2

    if total_pages <= visible_pages:
        start_page = 1
        end_page = total_pages
    else:
        if current_page <= half_visible:
            start_page = 1
            end_page = visible_pages
        elif current_page >= total_pages - half_visible:
            start_page = total_pages - visible_pages + 1
            end_page = total_pages
        else:
            start_page = current_page - half_visible
            end_page = current_page + half_visible

    pagination_elements = [
        # 이전 페이지 버튼
        html.Button(
            "이전",
            id='delivery-prev-page',
            style={
                **pagination_button_style,
                **pagination_button_hover_style,
                'opacity': '0.5' if current_page == 1 else '1',
                'cursor': 'not-allowed' if current_page == 1 else 'pointer',
            }
        ),
    ]

    # 페이지 번호 추가
    for page in range(start_page, end_page + 1):
        is_current = page == current_page
        pagination_elements.append(
            html.Button(
                str(page),
                style={
                    **pagination_button_style,
                    **pagination_button_hover_style,
                    **(current_page_style if is_current else {})
                }
            )
        )

    # 다음 페이지 버튼
    pagination_elements.append(
        html.Button(
            "다음",
            id='delivery-next-page',
            style={
                **pagination_button_style,
                **pagination_button_hover_style,
                'opacity': '0.5' if current_page == total_pages else '1',
                'cursor': 'not-allowed' if current_page == total_pages else 'pointer',
            }
        )
    )

    # 총 페이지 정보
    pagination_elements.append(
        html.Div(
            f"총 {total_pages} 페이지",
            style={
                'marginLeft': '1rem',
                'fontSize': '0.875rem',
                'color': '#64748b',
                'fontWeight': '500'
            }
        )
    )

    return pagination_elements