# layouts.py

from dash import html
import dash_bootstrap_components as dbc
from typing import Any
from .styles import StyleManager


class LayoutManager:
    """레이아웃 관리를 위한 최적화된 클래스"""

    @staticmethod
    def create_page_layout(content: Any) -> html.Div:
        """
        페이지 레이아웃 생성 - 네비게이션과 컨텐츠 영역 분리

        Args:
            content: 페이지 컨텐츠
        Returns:
            html.Div: 구조화된 레이아웃
        """
        styles = StyleManager.get_common_styles()
        return html.Div([
            # 상단 여백 추가로 네비게이션바와 분리
            html.Div(style={'height': '80px'}),
            # 컨텐츠 영역
            dbc.Container([
                dbc.Card([
                    dbc.CardBody(content)
                ], style=styles['card'])
            ], fluid=True, style={'padding': '20px'})
        ], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

    @staticmethod
    def create_navbar(active_path: str) -> dbc.Navbar:
        """
        네비게이션 바 생성 - 고정 포지션 적용

        Args:
            active_path: 현재 활성화된 경로
        Returns:
            dbc.Navbar: 스타일링된 네비게이션바
        """
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
                        active=is_active,
                        style={
                            "color": "#FFFFFF" if is_active else "#000000",
                            "backgroundColor": "#007BFF" if is_active else "transparent",
                            "borderRadius": "4px",
                            "padding": "0.75rem 1.25rem",
                            "margin": "0 0.5rem",
                            "fontWeight": "500",
                            "transition": "all 0.2s ease-in-out",
                        }
                    )
                )
            )

        return dbc.Navbar(
            dbc.Container([
                dbc.NavbarBrand("배송 관리 시스템", style={"fontSize": "1.5rem", "fontWeight": "bold"}),
                dbc.Nav(nav_links, navbar=True),
            ], fluid=True),
            color="white",
            dark=False,
            fixed="top",  # 네비게이션 바 고정
            style={
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                "height": "60px",
                "zIndex": "1000"
            }
        )