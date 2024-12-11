
from typing import Optional, Dict, Any, List
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dataclasses import dataclass


@dataclass
class SearchRefreshConfig:
    """검색/새로고침 설정 구조체"""
    placeholder: str = '검색어를 입력하세요'
    refresh_text: str = '새로고침'
    debounce_ms: int = 500
    min_width: str = '130px'


class DashComponents:
    """고도화된 대시보드 컴포넌트 시스템"""

    @staticmethod
    def create_search_refresh_section(
            search_id: str,
            refresh_id: str,
            config: Optional[SearchRefreshConfig] = None
    ) -> html.Div:
        """
        검색 및 새로고침 섹션 생성기

        Args:
            search_id (str): 검색 입력창 ID
            refresh_id (str): 새로고침 버튼 ID
            config (Optional[SearchRefreshConfig]): 커스텀 설정

        Returns:
            html.Div: 최적화된 검색/새로고침 섹션
        """
        if config is None:
            config = SearchRefreshConfig()

        button_style = {
            'minWidth': config.min_width,
            'height': '42px',
            'fontSize': '14px',
            'fontWeight': '500',
            'borderRadius': '8px',
            'backgroundColor': '#3b82f6',
            'border': 'none',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'color': 'white',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'gap': '8px',
            'transition': 'all 0.2s ease',
            'cursor': 'pointer'
        }

        input_style = {
            'width': '300px',
            'height': '42px',
            'fontSize': '14px',
            'borderRadius': '8px',
            'border': '1px solid #e2e8f0',
            'padding': '0 16px',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.05)',
            'transition': 'all 0.2s ease'
        }

        container_style = {
            'display': 'flex',
            'alignItems': 'center',
            'gap': '12px',
            'marginBottom': '20px',
            'width': '100%'
        }

        return html.Div([
            dbc.Button(
                children=[
                    html.I(className="fas fa-sync-alt", style={'marginRight': '8px'}),
                    config.refresh_text
                ],
                id=refresh_id,
                color="primary",
                style=button_style,
                className='refresh-button'
            ),
            dbc.Input(
                id=search_id,
                type="text",
                placeholder=config.placeholder,
                style=input_style,
                className='search-input',
                debounce=True
            )
        ], style=container_style)

    @staticmethod
    def create_data_table(
            table_id: str,
            columns: List[Dict[str, str]],
            data: List[Dict[str, Any]]
    ) -> dash_table.DataTable:
        """데이터 테이블 생성 (기존 구현 유지)"""
        return dash_table.DataTable(...)  # 이전 구현 내용 유지