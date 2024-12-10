import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from src.dash_views.common import COLORS, create_pie_chart, create_stat_row, status_color_map
from src.dash_views.delivery_page import delivery_layout
from src.dash_views.driver_page import generate_sample_driver_data, driver_layout

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

header = dbc.Container([
    html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("배송 관리 시스템",
                        style={'color': COLORS['text_primary'],
                               'fontWeight': '600',
                               'textAlign': 'center'})
            ], width=12)
        ], className="mb-2"),
        dbc.Row([
            dbc.Col([], width=9),
            dbc.Col([
                html.Div([
                    dbc.Button("새로고침", color="primary", className="me-2", style={'float': 'right'}),
                    html.Br(),
                    html.Div("마지막 업데이트: 방금",
                             style={
                                 'fontSize': '0.8rem',
                                 'textAlign': 'right',
                                 'color': COLORS['text_secondary'],
                                 'marginTop': '1rem'
                             })
                ], style={'textAlign': 'right'})
            ], width=3)
        ])
    ])
], fluid=True)

tabs = dbc.Tabs([
    dbc.Tab(label="대시보드", tab_id="tab-main"),
    dbc.Tab(label="배송 현황", tab_id="tab-delivery"),
    dbc.Tab(label="기사 현황", tab_id="tab-driver")
], id="tabs", active_tab="tab-main")

blue_line = html.Hr(style={'borderColor': COLORS['primary'], 'borderWidth': '2px', 'marginTop': '0'})

def get_driver_state_counts():
    df = generate_sample_driver_data()
    counts = df['상태(Status)'].value_counts()
    return counts.to_dict()

def create_main_driver_cards(counts):
    cards = []
    for status, count in counts.items():
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

dashboard_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4("배송 현황", className="mb-3", style={'textAlign': 'center', 'fontWeight': 'bold'}),
            create_stat_row(50, 12, 38),
            # 배송현황: 대기=파랑, 배송중=노랑, 배송완료=초록
            dcc.Graph(id='delivery-pie-chart', style={'marginTop': '2rem'})
        ], width=6, style={'borderRight': f'1px solid {COLORS["bg_primary"]}'}),
        dbc.Col([
            html.H4("기사 현황", className="mb-3", style={'textAlign': 'center', 'fontWeight': 'bold'}),
            html.Div(id='driver-state-cards-main'),
            # 기사현황: 대기=파랑, 배송중=노랑, 복귀중=하늘색, 퇴근=빨강
            # 파이차트도 status_color_map 사용하므로 카드 색상과 동일
            dcc.Graph(id='driver-pie-chart', style={'marginTop': '2rem'})
        ], width=6)
    ], style={'marginTop': '2rem'})
], fluid=True)

app.layout = dbc.Container([
    header,
    tabs,
    blue_line,
    html.Div(id='tab-content', className='p-4'),
    dcc.Interval(id='interval-component', interval=10000, n_intervals=0)
], fluid=True)

@callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'active_tab')]
)
def render_tab_content(active_tab):
    if active_tab == "tab-main":
        return dashboard_layout
    elif active_tab == "tab-delivery":
        return delivery_layout
    elif active_tab == "tab-driver":
        return driver_layout
    return html.Div("탭을 선택해주세요.")

@callback(
    Output('delivery-pie-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_delivery_pie_chart(n):
    delivery_status_data = {
        '대기': 12,
        '배송중': 15,
        '배송완료': 23
    }
    return create_pie_chart(delivery_status_data, "배송 현황")

@callback(
    Output('driver-pie-chart', 'figure'),
    Output('driver-state-cards-main', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_driver_pie_chart_and_cards(n):
    counts = get_driver_state_counts()
    fig = create_pie_chart(counts, "기사 현황")
    cards = create_main_driver_cards(counts)
    return fig, cards

if __name__ == '__main__':
    app.run_server(debug=True)
