from dash import html
import dash_bootstrap_components as dbc


def create_navbar():
    notifications = [
        {
            "type": "danger",
            "time": "방금 전",
            "message": "ETA 초과된 배송이 3건 있습니다.",
            "icon": "fas fa-exclamation-circle"
        },
        {
            "type": "warning",
            "time": "10분 전",
            "message": "ETA 임박한 배송이 5건 있습니다.",
            "icon": "fas fa-clock"
        },
        {
            "type": "info",
            "time": "30분 전",
            "message": "'김운송' 기사님이 배송을 시작했습니다.",
            "icon": "fas fa-truck"
        }
    ]

    notification_items = [
        dbc.DropdownMenuItem([
            html.I(className=notif["icon"], style={"color": get_notification_color(notif["type"])}),
            html.Div([
                html.Div(notif["message"], className="ms-3"),
                html.Small(notif["time"], className="text-muted ms-3")
            ], className="flex-grow-1"),
        ], className="d-flex align-items-center py-2")
        for notif in notifications
    ]

    return dbc.Navbar(
        dbc.Container([
            # 로고 영역
            html.A(
                dbc.Row([
                    dbc.Col(dbc.NavbarBrand("Delivery Dashboard", className="ms-2")),
                ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            # 네비게이션 링크
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Main", href="/")),
                dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
                dbc.NavItem(dbc.NavLink("KPI", href="/kpi")),
            ], className="ms-auto me-3"),
            # 알림 드롭다운 부분 수정
            dbc.Nav([
                dbc.DropdownMenu(
                    children=notification_items,
                    label=html.Span([
                        html.I(className="fas fa-bell", style={"color": "white"}),  # 색상을 하얀색으로 변경
                        dbc.Badge(
                            "3",
                            color="danger",
                            pill=True,
                            className="position-absolute top-0 start-100 translate-middle"
                        ),
                    ], className="position-relative"),
                    align_end=True,
                    className="me-2"
                ),
            ], navbar=True)
        ], fluid=True),
        dark=True,  # 어두운 테마 적용으로 하얀색 아이콘이 잘 보이도록
        className="mb-4 shadow-sm"
    )


def get_notification_color(type):
    color_map = {
        "danger": "#dc2626",
        "warning": "#d97706",
        "info": "#2563eb",
    }
    return color_map.get(type, "#6b7280")
