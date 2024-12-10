import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Enhanced UI/UX Color System
COLORS = {
    'primary': '#0062ff',  # Reverted to original blue
    'secondary': '#393939',  # Dark Grey for text
    'success': '#24a148',  # Green
    'warning': '#f1c21b',  # Yellow
    'error': '#da1e28',  # Red
    'info': '#4589ff',  # Light Blue

    'bg_primary': '#f4f4f4',  # Light Grey
    'bg_secondary': '#ffffff',  # White

    'text_primary': '#161616',  # Almost Black
    'text_secondary': '#525252',  # Grey
}

# Font Configurations
FONTS = {
    'primary': 'IBM Plex Sans, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, Open Sans, Helvetica Neue, sans-serif',
}


def generate_sample_delivery_data():
    """Generate sample delivery data"""
    departments = ['Logistics', 'Express', 'Special Delivery']
    operation_types = ['배송', '회수']
    delivery_types = ['방문수령', '대리수령', '무인함']
    statuses = ['대기', '배송중', '배송완료']

    data = []
    for _ in range(50):
        depart_time = datetime.now() - timedelta(hours=random.randint(0, 24))
        arrive_time = depart_time + timedelta(hours=random.randint(1, 4))
        eta = depart_time + timedelta(hours=random.randint(2, 5))

        delivery = {
            'OperationType': random.choice(operation_types),
            'Department': random.choice(departments),
            'DeliveryType': random.choice(delivery_types),
            'DepartTime': depart_time.strftime('%H:%M'),
            'ArriveTime': arrive_time.strftime('%H:%M'),
            'DeliveryDuration': f"{random.randint(30, 120)}분",
            'Status': random.choice(statuses),
            'DPS': f'DPS{random.randint(1000, 9999)}',
            'ETA': eta.strftime('%Y-%m-%d %H:%M'),
            'SLA': random.choice(['CS', 'HES', 'Lenovo']),
            'Address': f'{random.randint(1, 100)} Street, City',
            'ZipCode': f'{random.randint(10000, 99999)}',
            'Recipient': f'수령인 {random.randint(1, 100)}',
            'Contact': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}'
        }
        data.append(delivery)

    return pd.DataFrame(data)


def generate_sample_driver_data():
    """Generate sample driver data"""
    departments = ['Logistics', 'Express', 'Special Delivery']
    vehicle_types = ['모터사이클', '밴', '트럭']
    statuses = ['대기', '배송중', '복귀중', '퇴근']

    data = []
    for i in range(30):
        arrive_time = datetime.now() + timedelta(hours=random.randint(1, 12))
        driver = {
            'Department': random.choice(departments),
            'Name': f'기사 {i + 1}',
            'ArriveTime': arrive_time.strftime('%Y-%m-%d %H:%M'),
            'VehicleType': random.choice(vehicle_types),
            'Status': random.choice(statuses),
            'TelNumber': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}'
        }
        data.append(driver)

    return pd.DataFrame(data)


def create_pie_chart(data, title):
    """Create a pie chart with given data"""
    labels = list(data.keys())
    values = list(data.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=[COLORS['primary'], COLORS['success'], COLORS['warning']]
    )])

    fig.update_layout(
        title=title,
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig


def create_stat_row(total, in_progress, completed):
    """Create a horizontal row of statistics"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("총 건수", className="text-muted"),
                    html.H4(str(total), style={'color': COLORS['primary']})
                ])
            ], className="mb-2")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("진행중", className="text-muted"),
                    html.H4(str(in_progress), style={'color': COLORS['warning']})
                ])
            ], className="mb-2")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("완료", className="text-muted"),
                    html.H4(str(completed), style={'color': COLORS['success']})
                ])
            ], className="mb-2")
        ], width=4)
    ], className="mb-3")


# Initialize Dash App
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

# Main Layout
app.layout = dbc.Container([
    # Header
    html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("배송 관리 시스템",
                        style={'color': COLORS['text_primary'], 'fontWeight': '600'})
            ], width=6),
            dbc.Col([
                html.Div([
                    dbc.Button("새로고침", color="primary", className="me-2"),
                    html.Span("마지막 업데이트: 방금")
                ], style={'textAlign': 'right'})
            ], width=6)
        ], className="mb-4")
    ], style={'borderBottom': f'3px solid {COLORS["primary"]}', 'padding': '1rem 0'}),

    # Tabs
    dbc.Tabs([
        # 대시보드 Tab
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    html.H4("배송 현황", className="mb-3"),
                    create_stat_row(50, 12, 38),
                    dcc.Graph(id='delivery-pie-chart')
                ], width=6),
                dbc.Col([
                    html.H4("기사 현황", className="mb-3"),
                    create_stat_row(30, 15, 15),
                    dcc.Graph(id='driver-pie-chart')
                ], width=6)
            ])
        ], label="대시보드", tab_id="tab-main"),

        # 배송 현황 Tab
        dbc.Tab([
            create_stat_row(50, 12, 38),
            html.Div(id='delivery-table')
        ], label="배송 현황", tab_id="tab-delivery"),

        # 기사 현황 Tab
        dbc.Tab([
            create_stat_row(30, 15, 15),
            html.Div(id='driver-table')
        ], label="기사 현황", tab_id="tab-driver")
    ], id="tabs", active_tab="tab-main"),

    # Interval for periodic updates
    dcc.Interval(id='interval-component', interval=10000, n_intervals=0)
], fluid=True)


# Callback for delivery pie chart
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


# Callback for driver pie chart
@callback(
    Output('driver-pie-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_driver_pie_chart(n):
    driver_status_data = {
        '대기': 8,
        '배송중': 12,
        '복귀중': 5
    }
    return create_pie_chart(driver_status_data, "기사 현황")


# Callback to update delivery table
@callback(
    Output('delivery-table', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_delivery_table(n):
    df = generate_sample_delivery_data()
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)


# Callback to update driver table
@callback(
    Output('driver-table', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_driver_table(n):
    df = generate_sample_driver_data()
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)


if __name__ == '__main__':
    app.run_server(debug=True)