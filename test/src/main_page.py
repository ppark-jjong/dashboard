from dash import html, dcc
import dash_bootstrap_components as dbc
from src.dash_views.data_generate import DataGenerator
from src.dash_views.components import DashboardComponents, DashboardCharts
from src.dash_views.styles import StyleManager


def create_main_dashboard():
    delivery_metrics = DataGenerator.get_delivery_metrics()
    rider_metrics = DataGenerator.get_rider_metrics()
    styles = StyleManager.get_common_styles()

    return html.Div([
        dbc.Container([
            # 메트릭스 카드 섹션
            dbc.Row([
                dbc.Col(
                    DashboardComponents.create_stats_card(
                        "총 배송건수",
                        f"{delivery_metrics.total_count:,}건",
                        "전체 배송 물량"
                    ), width=12, lg=3
                ),
                dbc.Col(
                    DashboardComponents.create_stats_card(
                        "완료율",
                        delivery_metrics.completion_rate,
                        "배송 완료율"
                    ), width=12, lg=3
                ),
                dbc.Col(
                    DashboardComponents.create_stats_card(
                        "활동 기사",
                        f"{rider_metrics['active_riders']}명",
                        "현재 배송중"
                    ), width=12, lg=3
                ),
                dbc.Col(
                    DashboardComponents.create_stats_card(
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
    ], style=styles['container'])
