# pages/kpi.py
from dash import register_page, html
import dash_bootstrap_components as dbc
from .mock_data import generate_sample_data
import pandas as pd

register_page(__name__, path='/kpi')

def create_kpi_card(title, value, subtitle):
    return dbc.Card([
        dbc.CardBody([
            html.H4(title, className="text-muted mb-3"),
            html.H2(value, className="mb-2"),
            html.P(subtitle, className="text-muted mb-0")
        ])
    ], className="shadow-sm h-100")

def layout():
    # 데이터 생성 및 처리
    data = generate_sample_data(200)
    df = pd.DataFrame(data)
    
    # KPI 계산
    total_deliveries = len(df)
    completed_rate = f"{(len(df[df['status'] == 2]) / total_deliveries * 100):.1f}%"
    issue_rate = f"{(len(df[df['status'] == 3]) / total_deliveries * 100):.1f}%"
    
    return html.Div([
        html.H1("KPI 대시보드", className="dashboard-title mb-4"),
        
        dbc.Row([
            dbc.Col([
                create_kpi_card(
                    "총 배송 건수",
                    f"{total_deliveries:,}",
                    "전체 배송 주문"
                )
            ], width=4),
            dbc.Col([
                create_kpi_card(
                    "배송 완료율",
                    completed_rate,
                    "완료된 배송 비율"
                )
            ], width=4),
            dbc.Col([
                create_kpi_card(
                    "이슈 발생률",
                    issue_rate,
                    "이슈가 발생한 배송 비율"
                )
            ], width=4),
        ], className="mb-4 g-4"),
        
        # 추가 KPI 섹션들...
    ])