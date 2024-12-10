import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html

COLORS = {
    'primary': '#0062ff',   # 파랑(대기)
    'secondary': '#393939',
    'success': '#24a148',   # 초록(배송완료)
    'warning': '#f1c21b',   # 노랑(배송중)
    'error': '#da1e28',     # 빨강(퇴근)
    'info': '#4589ff',      # 하늘색(복귀중)
    'bg_primary': '#f4f4f4',
    'bg_secondary': '#ffffff',
    'text_primary': '#161616',
    'text_secondary': '#525252',
}

FONTS = {
    'primary': 'IBM Plex Sans, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, Open Sans, Helvetica Neue, sans-serif',
}

# 상태별 색상 통일
# 대기: primary(파랑), 배송중: warning(노랑), 배송완료: success(초록), 복귀중: info(하늘색), 퇴근: error(빨강)
status_color_map = {
    '대기': COLORS['primary'],
    '배송중': COLORS['warning'],
    '복귀중': COLORS['info'],
    '퇴근': COLORS['error'],
    '배송완료': COLORS['success']
}

def create_pie_chart(data, title):
    # data는 {상태:값} 형태
    # 상태를 특정 순서로 정렬 필요 시 아래처럼 순서 정의 가능, 필요 없다면 그냥 이 상태 유지
    # 여기서는 색상만 통일하면 되므로 굳이 정렬 안해도 됨. 원한다면 상태별 우선순위가 있으면 정렬
    labels = list(data.keys())
    values = list(data.values())

    # 상태별로 색상 매핑
    colors = [status_color_map.get(s, COLORS['primary']) for s in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors
    )])

    fig.update_layout(
        title=title,
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_stat_row(total, in_progress, completed):
    card_style = {
        'textAlign': 'center',
        'fontSize': '1.4rem',
        'padding': '1rem'
    }

    title_style = {
        'fontSize': '1.1rem',
        'color': COLORS['text_secondary']
    }

    value_style = {
        'color': COLORS['primary'],
        'fontSize': '1.8rem',
        'fontWeight': 'bold'
    }

    total_card = dbc.Card([
        dbc.CardBody([
            html.H6("총 건수", className="text-muted", style=title_style),
            html.H4(str(total), style=value_style)
        ], style=card_style)
    ], className="mb-2", style={'borderRadius': '5px', 'border': f'1px solid {COLORS["bg_primary"]}'})

    in_progress_card = dbc.Card([
        dbc.CardBody([
            html.H6("진행중", className="text-muted", style=title_style),
            html.H4(str(in_progress), style={**value_style, 'color': COLORS['warning']})
        ], style=card_style)
    ], className="mb-2", style={'borderRadius': '5px', 'border': f'1px solid {COLORS["bg_primary"]}'})

    completed_card = dbc.Card([
        dbc.CardBody([
            html.H6("완료", className="text-muted", style=title_style),
            html.H4(str(completed), style={**value_style, 'color': COLORS['success']})
        ], style=card_style)
    ], className="mb-2", style={'borderRadius': '5px', 'border': f'1px solid {COLORS["bg_primary"]}'})

    return dbc.Row([
        dbc.Col([total_card], width=4),
        dbc.Col([in_progress_card], width=4),
        dbc.Col([completed_card], width=4)
    ], className="mb-3", style={'marginTop': '1rem', 'marginBottom': '1rem'})
