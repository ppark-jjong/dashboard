from dash import html, dcc, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from datetime import datetime
from typing import Dict, Any, List, Tuple


def create_status_badge(status: int) -> html.Span:
    """상태 배지 컴포넌트 생성

    Args:
        status (int): 상태 코드 (0: 대기, 1: 진행, 2: 완료, 3: 이슈)

    Returns:
        html.Span: 스타일이 적용된 상태 배지 컴포넌트
    """
    status_styles = {
        0: {'backgroundColor': '#fef9c3', 'color': '#854d0e'},  # 대기
        1: {'backgroundColor': '#dbeafe', 'color': '#1e40af'},  # 진행
        2: {'backgroundColor': '#dcfce7', 'color': '#166534'},  # 완료
        3: {'backgroundColor': '#fee2e2', 'color': '#991b1b'}  # 이슈
    }
    status_names = {0: '대기', 1: '진행', 2: '완료', 3: '이슈'}

    return html.Span(
        status_names[status],
        style={
            'padding': '4px 12px',
            'borderRadius': '12px',
            'fontSize': '0.875rem',
            'fontWeight': '500',
            **status_styles[status]
        }
    )


def create_info_section(label: str, value: Any, is_status: bool = False) -> html.Span:
    """정보 섹션 컴포넌트 생성

    Args:
        label (str): 레이블 텍스트
        value (Any): 표시할 값
        is_status (bool): 상태 표시 여부

    Returns:
        html.Span: 정보 섹션 컴포넌트
    """
    if is_status:
        display_value = create_status_badge(value)
    else:
        display_value = value or '-'

    return html.Span([
        html.Span(
            f"{label}: ",
            style={'color': '#64748b', 'marginRight': '8px', 'fontWeight': '500'}
        ),
        html.Span(
            display_value,
            style={'marginRight': '24px', 'color': '#0f172a'}
        )
    ])


def create_detail_panel():
    """상세 정보 패널 컴포넌트 생성"""
    return html.Div([
        # 현재 선택된 row의 ID를 저장하기 위한 저장소
        dcc.Store(id='current-row-id'),

        # 상세 정보 모달
        dbc.Modal([
            dbc.ModalHeader(
                html.H5("배송 상세 정보", className='modal-title')
            ),
            dbc.ModalBody([
                # 상태 변경 드롭다운
                html.Div(
                    className='status-change-section',
                    children=[
                        html.Label("상태 변경", className='status-label'),
                        dcc.Dropdown(
                            id='status-select',
                            options=[
                                {'label': '대기', 'value': 0},
                                {'label': '진행', 'value': 1},
                                {'label': '완료', 'value': 2},
                                {'label': '이슈', 'value': 3}
                            ],
                            className='status-dropdown'
                        ),
                    ]
                ),

                # 상세 정보 표시 영역
                html.Div(id='detail-info-container', className='detail-info-container'),

                # 이슈 사유 입력 (상태가 '이슈'일 때만 표시)
                html.Div(
                    id='issue-reason-container',
                    style={'display': 'none'},
                    children=[
                        html.Label("이슈 사유", className='issue-label'),
                        dbc.Input(
                            id='issue-reason-input',
                            type='text',
                            placeholder='이슈 사유를 입력하세요'
                        )
                    ]
                )
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "상태 변경",
                    id="update-status-btn",
                    className="update-status-btn"
                ),
                dbc.Button(
                    "닫기",
                    id="close-detail-modal",
                    className="close-modal-btn"
                )
            ])
        ], id='detail-modal', className='custom-modal')
    ])


# 콜백: 상태 변경 시 이슈 사유 입력 필드 표시/숨김
@callback(
    [Output('issue-reason-container', 'style'),
     Output('issue-reason-input', 'required')],
    Input('status-select', 'value')
)
def toggle_issue_reason(status: int) -> Tuple[Dict[str, str], bool]:
    """상태 변경에 따른 이슈 사유 입력 필드 토글

    Args:
        status (int): 선택된 상태 값

    Returns:
        Tuple[Dict[str, str], bool]: 스타일 딕셔너리와 필수 입력 여부
    """
    if status == 3:  # 이슈 상태
        return {'display': 'block', 'marginTop': '1rem'}, True
    return {'display': 'none'}, False


# 콜백: 상태 업데이트
@callback(
    [Output('delivery-table', 'data', allow_duplicate=True),
     Output('detail-modal', 'is_open'),
     Output('status-update-toast', 'is_open')],
    Input('update-status-btn', 'n_clicks'),
    [State('status-select', 'value'),
     State('issue-reason-input', 'value'),
     State('current-row-id', 'data'),
     State('delivery-table', 'data')],
    prevent_initial_call=True
)
def update_status(n_clicks: int, new_status: int, issue_reason: str,
                  current_row_id: int, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], bool, bool]:
    """상태 업데이트 처리

    Args:
        n_clicks (int): 버튼 클릭 횟수
        new_status (int): 새로운 상태 값
        issue_reason (str): 이슈 사유
        current_row_id (int): 현재 선택된 행 ID
        data (List[Dict[str, Any]]): 테이블 데이터

    Returns:
        Tuple[List[Dict[str, Any]], bool, bool]: 업데이트된 데이터, 모달 표시 여부, 토스트 표시 여부
    """
    if not n_clicks or new_status is None or current_row_id is None:
        return no_update, no_update, False

    new_data = data.copy()
    new_data[current_row_id]['status'] = new_status
    if new_status == 3:  # 이슈 상태
        new_data[current_row_id]['reason'] = issue_reason

    return sort_data(new_data), False, True