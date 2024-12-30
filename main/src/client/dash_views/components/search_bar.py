from dash import html, dcc, Input, Output, callback
from typing import Optional
import re


def create_search_bar() -> html.Div:
    """
    고성능 검색 바 컴포넌트 생성
    - 디바운싱 적용
    - 최적화된 검색 로직
    - 향상된 UX
    """
    return html.Div(
        className='search-section',
        children=[
            dcc.Input(
                id='search-input',
                type='text',
                placeholder='DPS번호, 배송기사, 주소로 검색...',
                className='search-input',
                debounce=True,  # 디바운싱 적용
                n_submit=0,  # Enter 키 이벤트 처리
                spellCheck=False,  # 성능 최적화
            ),
            # 검색 결과 카운트 표시
            html.Div(
                id='search-count',
                className='search-count'
            )
        ]
    )


@callback(
    Output('search-count', 'children'),
    [Input('delivery-table', 'data'),
     Input('search-input', 'value')]
)
def update_search_count(data: list, search_value: Optional[str]) -> str:
    """
    검색 결과 카운트 업데이트
    - 최적화된 필터링 로직
    - 실시간 결과 반영
    """
    if not search_value:
        return ""

    filtered_count = len([
        row for row in data
        if any(
            str(value).lower().find(search_value.lower()) != -1
            for value in row.values()
        )
    ])

    return f"검색 결과: {filtered_count}건"


def normalize_search_text(text: str) -> str:
    """
    검색어 정규화
    - 특수문자 처리
    - 공백 정규화
    - 대소문자 통일
    """
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    return text.lower()