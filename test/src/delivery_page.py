import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, callback, Output, Input, dcc, State


def generate_sample_delivery_data():
    data = [
        {
            'No.': idx + 1,
            '배송종류': '배송',
            '담당부서': 'Logistics',
            '배송유형': '방문수령',
            'DPS': f'DPS{1000 + idx}',
            '상태': ['대기', '배송중', '배송완료'][idx % 3],
            'ETA': f'2024-12-10 {9 + idx % 8}:30',
            '출발시간': f'{8 + idx % 8}:15',
            '주소': f'{idx + 10} Street, City',
            '수령인': f'수령인 {chr(65 + idx % 26)}철수',
            '연락처': f'010-{1000 + idx % 9000:04d}'
        }
        for idx in range(50)
    ]
    return pd.DataFrame(data)


def create_delivery_card(delivery):
    """
    Create a card for each delivery item
    """
    status_color = {
        '대기': 'warning',
        '배송중': 'primary',
        '배송완료': 'success'
    }

    return dbc.Card(
        dbc.CardBody([
            html.Div([
                # Header with No. and Status
                html.Div([
                    html.H5(f"No. {delivery['No.']}", className="card-title"),
                    dbc.Badge(
                        delivery['상태'],
                        color=status_color.get(delivery['상태'], 'secondary'),
                        className="ms-2"
                    )
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),

                # Delivery Details
                html.Hr(),
                html.P([
                    html.Strong("DPS: "), delivery['DPS']
                ]),
                html.P([
                    html.Strong("배송유형: "), delivery['배송유형']
                ]),
                html.P([
                    html.Strong("담당부서: "), delivery['담당부서']
                ]),
                html.P([
                    html.Strong("수령인: "), delivery['수령인']
                ]),
                html.P([
                    html.Strong("연락처: "), delivery['연락처']
                ]),

                # Footer with ETA and Address
                html.Hr(),
                html.Div([
                    html.Small([
                        html.Strong("도착예정: "),
                        delivery['ETA']
                    ], className="text-muted"),
                    html.Div([
                        html.Strong("주소: "),
                        delivery['주소']
                    ], style={'marginTop': '0.5rem'})
                ])
            ])
        ]),
        className="mb-3 shadow-sm",
        style={'borderRadius': '12px'}
    )


delivery_layout = [
    html.Div([
        # Search and Filter Section
        html.Div([
            dcc.Input(
                id='delivery-search-input',
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
            dbc.Button("검색", id='delivery-search-button', color="primary")
        ], style={'display': 'flex', 'justifyContent': 'flex-end', 'marginBottom': '1rem'}),

        # Card Grid Container
        html.Div(id='delivery-card-grid', style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fill, minmax(250px, 1fr))',
            'gap': '1rem'
        })
    ])
]


@callback(
    Output('delivery-card-grid', 'children'),
    [Input('delivery-search-button', 'n_clicks')],
    [State('delivery-search-input', 'value')]
)
def update_delivery_cards(n_clicks, search_value):
    df = generate_sample_delivery_data()

    if search_value:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_value, case=False).any(), axis=1)]

    # Convert DataFrame to list of cards
    cards = [create_delivery_card(row.to_dict()) for _, row in df.iterrows()]

    return cards