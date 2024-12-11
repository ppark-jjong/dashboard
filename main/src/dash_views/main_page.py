# main_page.py
import logging
from typing import Dict, Any
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from src.dash_views.components import DashComponents
from datetime import datetime
from src.dash_views.data_generate import DataGenerator


class DashboardComponents:
    """대시보드 공통 컴포넌트 관리 클래스"""

    @staticmethod
    def create_stats_card(title: str, value: str, description: str) -> dbc.Card:
        """통계 카드 컴포넌트 생성"""
        return dbc.Card([
            dbc.CardHeader(
                title,
                className="text-center",
                style={"backgroundColor": "white", "border": "none"}
            ),
            dbc.CardBody([
                html.H1(value, className="text-center text-primary"),
                html.P(description, className="text-center text-muted")
            ])
        ], className="mb-4", style={"border": "1px solid #eaeaea", "borderRadius": "8px"})


class DashboardCharts:
    """향상된 대시보드 차트 생성 클래스"""

    @staticmethod
    def create_delivery_status_pie() -> dcc.Graph:
        """배송 상태 원그래프 생성"""
        df = DataGenerator.generate_delivery_data()
        status_counts = df['상태'].value_counts()

        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=.3,
            marker=dict(colors=['#4CAF50', '#2196F3', '#FFC107']),
            textinfo='percent+label',
            textposition='inside',
            hovertemplate="상태: %{label}<br>건수: %{value}<br>비율: %{percent}<extra></extra>"
        )])

        fig.update_layout(
            title={
                'text': '배송 상태 분포',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=60, l=0, r=0, b=0),
            height=300,
            paper_bgcolor='white',
            plot_bgcolor='white'
        )

        return dcc.Graph(figure=fig)

    @staticmethod
    def create_rider_status_pie() -> dcc.Graph:
        """기사 상태 원그래프 생성"""
        df = DataGenerator.generate_rider_data()
        status_counts = df['상태'].value_counts()

        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=.3,
            marker=dict(colors=['#3F51B5', '#E91E63', '#FF9800']),
            textinfo='percent+label',
            textposition='inside',
            hovertemplate="상태: %{label}<br>인원: %{value}<br>비율: %{percent}<extra></extra>"
        )])

        fig.update_layout(
            title={
                'text': '기사 상태 분포',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=60, l=0, r=0, b=0),
            height=300,
            paper_bgcolor='white',
            plot_bgcolor='white'
        )

        return dcc.Graph(figure=fig)



def create_main_dashboard() -> html.Div:
    """메인 대시보드 레이아웃 v2.0"""
    try:
        delivery_metrics = DataGenerator.get_delivery_metrics()
        rider_metrics = DataGenerator.get_rider_metrics()

        return html.Div([
            dbc.Container([
                # 메트릭스 카드 섹션
                dbc.Row([
                    dbc.Col(
                        DashComponents.create_stats_card(
                            "총 배송건수",
                            str(delivery_metrics.total_count),
                            "전체 배송 물량"
                        ), width=12, lg=3
                    ),
                    dbc.Col(
                        DashComponents.create_stats_card(
                            "완료율",
                            delivery_metrics.completion_rate,
                            "배송 완료율"
                        ), width=12, lg=3
                    ),
                    dbc.Col(
                        DashComponents.create_stats_card(
                            "활동 기사",
                            str(rider_metrics['active_riders']),
                            "현재 배송중"
                        ), width=12, lg=3
                    ),
                    dbc.Col(
                        DashComponents.create_stats_card(
                            "평균 배송",
                            rider_metrics['avg_deliveries'],
                            "기사당 평균"
                        ), width=12, lg=3
                    )
                ], className="mb-4"),

                # 차트 섹션
                dbc.Row([
                    dbc.Col(
                        DashboardCharts.create_delivery_status_pie(),
                        width=12, lg=6, className="mb-4"
                    ),
                    dbc.Col(
                        DashboardCharts.create_rider_status_pie(),
                        width=12, lg=6, className="mb-4"
                    )
                ])
            ], fluid=True)
        ], style={'backgroundColor': 'white', 'padding': '2rem'})
    except Exception as e:
        logging.error(f"대시보드 생성 중 오류 발생: {str(e)}")
        return html.Div("데이터 로딩 중 오류가 발생했습니다.", className="text-danger p-3")
