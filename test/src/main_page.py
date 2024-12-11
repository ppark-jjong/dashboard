import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
from delivery_page import delivery_layout
from driver_page import rider_layout

# 글로벌 메뉴바 생성 함수
def create_navbar(active_path):
    nav_items = [
        {"label": "대시보드", "href": "/"},
        {"label": "배송 현황", "href": "/delivery"},
        {"label": "기사 현황", "href": "/rider"}
    ]

    nav_links = []
    for item in nav_items:
        is_active = active_path == item["href"]
        nav_links.append(
            dbc.NavItem(
                dbc.NavLink(
                    item["label"],
                    href=item["href"],
                    className="text-uppercase",
                    style={
                        "fontSize": "1rem",
                        "fontWeight": "bold",
                        "color": "#000000" if not is_active else "#FFFFFF",
                        "padding": "0.75rem 1.25rem",
                        "textDecoration": "none",
                        "backgroundColor": "#007BFF" if is_active else "transparent",
                        "borderRadius": "4px",
                        "transition": "all 0.2s ease-in-out",
                    }
                )
            )
        )

    return dbc.Navbar(
        dbc.Container([
            dbc.Nav(nav_links, pills=True, className="ml-auto"),
        ]),
        color="white",
        dark=False,
        style={
            "height": "60px",
            "boxShadow": "0 1px 2px rgba(0,0,0,0.1)"
        }
    )

# 메인 페이지 레이아웃
def create_main_dashboard():
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("총 배송 건수", className="text-center", style={"backgroundColor": "white", "border": "none"}),
                        dbc.CardBody([
                            html.H1("1000+", className="text-center text-primary"),
                            html.P("현재 배송 중인 전체 건수", className="text-center text-muted")
                        ])
                    ], className="mb-4", style={"border": "1px solid #eaeaea", "borderRadius": "8px"})
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("총 기사 수", className="text-center", style={"backgroundColor": "white", "border": "none"}),
                        dbc.CardBody([
                            html.H1("150", className="text-center text-primary"),
                            html.P("활동 중인 기사", className="text-center text-muted")
                        ])
                    ], className="mb-4", style={"border": "1px solid #eaeaea", "borderRadius": "8px"})
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("완료율", className="text-center", style={"backgroundColor": "white", "border": "none"}),
                        dbc.CardBody([
                            html.H1("75%", className="text-center text-success"),
                            html.P("현재 완료된 배송 비율", className="text-center text-muted")
                        ])
                    ], className="mb-4", style={"border": "1px solid #eaeaea", "borderRadius": "8px"})
                ], width=4)
            ]),

            # 추가적인 섹션 (예: 그래프)
            dbc.Row([
                dbc.Col([
                    html.Div("추가적인 내용 (그래프나 테이블)", style={"textAlign": "center", "padding": "1rem"})
                ])
            ])
        ], fluid=True)
    ])

# 애플리케이션 초기화
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 페이지 레이아웃
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='navbar', children=create_navbar("/")),
    html.Div(id='page-content', children=create_main_dashboard(), style={"backgroundColor": "white", "padding": "2rem"})
])

# 콜백: 메뉴 및 페이지 동적 렌더링
@app.callback(
    [Output('navbar', 'children'),
     Output('page-content', 'children')],
    [Input('url', 'pathname')]
)
def render_page(pathname):
    navbar = create_navbar(pathname)
    if pathname == "/delivery":
        return navbar, delivery_layout
    elif pathname == "/rider":
        return navbar, rider_layout
    else:
        return navbar, create_main_dashboard()

if __name__ == '__main__':
    app.run_server(debug=True)
