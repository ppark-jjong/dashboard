# pages/main.py
from dash import register_page, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from .mock_data import generate_sample_data

register_page(__name__, path='/')

def layout():
    # 샘플 데이터 생성
    data = generate_sample_data(200)  # 200개의 샘플 데이터
    df = pd.DataFrame(data)
    
    # 부서별 배송 현황
    dept_counts = df['department'].value_counts().reset_index()
    dept_counts.columns = ['department', 'count']
    
    dept_fig = go.Figure(data=[
        go.Bar(
            x=dept_counts['department'],
            y=dept_counts['count'],
            marker_color='#0f172a'
        )
    ])
    dept_fig.update_layout(
        title={
            'text': "부서별 배송 현황",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'color': '#0f172a'}
        },
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'color': '#475569'},
        margin=dict(t=80, b=40, l=40, r=40)
    )
    
    # 상태별 현황
    status_map = {0: '대기', 1: '진행', 2: '완료', 3: '이슈'}
    df['status_label'] = df['status'].map(status_map)
    status_counts = df['status_label'].value_counts()
    
    status_colors = {
        '대기': '#fef9c3',
        '진행': '#dbeafe',
        '완료': '#dcfce7',
        '이슈': '#fee2e2'
    }
    
    status_fig = go.Figure(data=[
        go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=.6,
            marker_colors=[status_colors[label] for label in status_counts.index]
        )
    ])
    status_fig.update_layout(
        title={
            'text': "상태별 배송 현황",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'color': '#0f172a'}
        },
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'color': '#475569'}
    )
    
    return html.Div([
        html.H1("배송 현황 개요", className="dashboard-title mb-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=dept_fig)
                    ])
                ], className="shadow-sm")
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=status_fig)
                    ])
                ], className="shadow-sm")
            ], width=6),
        ]),
        html.Div(className="mb-4"),  # 여백
    ])