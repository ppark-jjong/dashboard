import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import random
from datetime import datetime, timedelta
from delivery_page import generate_sample_delivery_data, delivery_layout
from driver_page import generate_sample_rider_data, rider_layout



# Sample data generation functions
def generate_sample_delivery_data(n=100):
    statuses = ['배송중', '배송완료', '대기']
    weights = [0.3, 0.5, 0.2]  # 30% 배송중, 50% 완료, 20% 대기

    data = {
        '배송번호': [f'DEL{i:04d}' for i in range(1, n + 1)],
        '상태': random.choices(statuses, weights=weights, k=n),
        '시간': [(datetime.now() - timedelta(minutes=random.randint(0, 300))).strftime('%Y-%m-%d %H:%M:%S') for _ in
               range(n)],
        '주소': [f'서울시 테스트구 샘플동 {random.randint(1, 100)}번길 {random.randint(1, 100)}' for _ in range(n)]
    }
    return pd.DataFrame(data)


def generate_sample_rider_data(n=30):
    statuses = ['배송중', '대기중', '복귀중', '퇴근']
    weights = [0.4, 0.2, 0.2, 0.2]  # 40% 배송중, 20% 대기중, 20% 복귀중, 20% 퇴근

    data = {
        '기사번호': [f'RID{i:03d}' for i in range(1, n + 1)],
        '이름': [f'기사{i}' for i in range(1, n + 1)],
        '상태': random.choices(statuses, weights=weights, k=n),
        '배달건수': [random.randint(0, 20) for _ in range(n)]
    }
    return pd.DataFrame(data)


def create_delivery_status_chart():
    df = generate_sample_delivery_data()
    status_counts = df['상태'].value_counts()

    colors = {
        '배송중': '#3b82f6',
        '배송완료': '#10b981',
        '대기': '#f43f5e'
    }

    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        hole=.7,
        marker_colors=[colors[status] for status in status_counts.index]
    )])

    fig.update_layout(
        title='배송 현황',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, l=0, r=0, b=0),
        height=300
    )

    fig.add_annotation(
        text=f'총 {len(df)}건',
        x=0.5, y=0.5,
        font=dict(size=20, color='#1f2937'),
        showarrow=False
    )

    return fig


def create_rider_status_chart():
    df = generate_sample_rider_data()
    status_counts = df['상태'].value_counts()

    colors = {
        '배송중': '#3b82f6',  # 파랑
        '대기중': '#f59e0b',  # 주황
        '복귀중': '#8b5cf6',  # 보라
        '퇴근': '#6b7280'  # 회색
    }

    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        hole=.7,
        marker_colors=[colors[status] for status in status_counts.index]
    )])

    fig.update_layout(
        title='기사 현황',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, l=0, r=0, b=0),
        height=300
    )

    fig.add_annotation(
        text=f'총 {len(df)}명',
        x=0.5, y=0.5,
        font=dict(size=20, color='#1f2937'),
        showarrow=False
    )

    return fig


def create_status_list(data, type_name='배송'):
    total = len(data)
    status_counts = data['상태'].value_counts()

    status_colors = {
        # 배송 현황 색상
        '배송중': '#3b82f6',
        '배송완료': '#10b981',
        '대기': '#f43f5e',
        # 기사 현황 색상
        '대기중': '#f59e0b',
        '복귀중': '#8b5cf6',
        '퇴근': '#6b7280'
    }

    return html.Div([
        *[html.Div([
            html.Div([
                html.Div(style={
                    'width': '12px',
                    'height': '12px',
                    'borderRadius': '50%',
                    'backgroundColor': status_colors[status],
                    'marginRight': '8px'
                }),
                html.Span(status, style={'color': '#4b5563'})
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                html.Span(f"{count:,}건" if type_name == '배송' else f"{count:,}명",
                          style={'fontWeight': 'bold', 'marginRight': '8px'}),
                html.Span(f"({count / total * 100:.1f}%)",
                          style={'color': '#6b7280'})
            ])
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'padding': '12px 0',
            'borderBottom': '1px solid #e5e7eb'
        }) for status, count in status_counts.items()]
    ], style={
        'backgroundColor': 'white',
        'padding': '16px',
        'borderRadius': '8px',
        'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
    })


def create_dashboard_layout():
    return html.Div([
        dbc.Row([
            # Delivery Status Section
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("배송 현황", className="mb-0"),
                        style={'backgroundColor': 'white', 'borderBottom': '1px solid #e5e7eb'}
                    ),
                    dbc.CardBody([
                        dcc.Graph(
                            id='delivery-status-chart',
                            figure=create_delivery_status_chart(),
                            config={'displayModeBar': False}
                        ),
                        html.Div(
                            id='delivery-status-list',
                            style={'marginTop': '20px'}
                        )
                    ])
                ], style={'marginBottom': '1rem'})
            ], width=6),

            # Rider Status Section
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("기사 현황", className="mb-0"),
                        style={'backgroundColor': 'white', 'borderBottom': '1px solid #e5e7eb'}
                    ),
                    dbc.CardBody([
                        dcc.Graph(
                            id='rider-status-chart',
                            figure=create_rider_status_chart(),
                            config={'displayModeBar': False}
                        ),
                        html.Div(
                            id='rider-status-list',
                            style={'marginTop': '20px'}
                        )
                    ])
                ], style={'marginBottom': '1rem'})
            ], width=6)
        ]),

        dcc.Interval(
            id='interval-component',
            interval=60 * 1000,  # 1분마다 업데이트
            n_intervals=0
        )
    ])


@callback(
    [Output('delivery-status-chart', 'figure'),
     Output('delivery-status-list', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_delivery_section(n):
    df = generate_sample_delivery_data()
    return create_delivery_status_chart(), create_status_list(df, '배송')


@callback(
    [Output('rider-status-chart', 'figure'),
     Output('rider-status-list', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_rider_section(n):
    df = generate_sample_rider_data()
    return create_rider_status_chart(), create_status_list(df, '기사')


# Main dashboard layout
dashboard_layout = create_dashboard_layout()

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Define the app layout with tabs
app.layout = dbc.Container([
    html.H1("배송 관리 대시보드",
            className="text-center my-4",
            style={'color': '#1f2937', 'fontWeight': 'bold'}),

    dbc.Tabs([
        dbc.Tab(dashboard_layout, label="대시보드"),
        dbc.Tab(delivery_layout, label="배송 현황"),
        dbc.Tab(rider_layout, label="기사 현황")
    ], style={'marginBottom': '20px'})
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)