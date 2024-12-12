# app.py
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import data_generator as dg
from components import create_navbar
import main_page
import delivery_page
import driver_page

# 커스텀 CSS 스타일 정의
custom_style = '''
body {
    min-height: 100vh;
    background-color: #f8fafc;
}

.page-container {
    width: 100%;
    max-width: 100%;
    padding: 1.5rem;
}

.data-table-container {
    background: white;
    padding: 20px;
    border-radius: 12px;
    width: 100%;
}

.form-control:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 0.2rem rgba(37, 99, 235, 0.25);
}

.btn-primary {
    background-color: #2563eb;
    border-color: #2563eb;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    background-color: #1d4ed8;
    border-color: #1d4ed8;
    transform: translateY(-1px);
}

.btn-outline-primary {
    color: #2563eb;
    border-color: #2563eb;
    transition: all 0.3s ease;
}

.btn-outline-primary:hover {
    background-color: #2563eb;
    color: white;
    transform: translateY(-1px);
}

/* 네비게이션 스타일 */
.nav-link {
    position: relative;
    transition: color 0.3s ease;
}

.nav-link:hover {
    color: #2563eb !important;
}

.nav-link::after {
    content: '';
    position: absolute;
    width: 0;
    height: 2px;
    bottom: 0;
    left: 0;
    background-color: #2563eb;
    transition: width 0.3s ease;
}

.nav-link:hover::after {
    width: 100%;
}

.nav-link.active {
    color: #2563eb !important;
}

.nav-link.active::after {
    width: 100%;
}

/* 테이블 스타일링 */
.dash-table-container {
    width: 100% !important;
}

.dash-spreadsheet-container {
    width: 100% !important;
}

.dash-spreadsheet {
    width: 100% !important;
}

.dash-fixed-content {
    width: 100% !important;
}

/* 페이지네이션 스타일링 */
.dash-table-container .previous-next-container {
    margin-top: 16px !important;
    padding-top: 16px !important;
    border-top: 1px solid #e2e8f0 !important;
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;
}

.dash-table-container .previous-next-container button {
    background-color: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
    margin: 0 4px !important;
    color: #475569 !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
}

.dash-table-container .previous-next-container button:hover {
    background-color: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
}

.dash-table-container .page-number {
    background-color: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
    margin: 0 4px !important;
    color: #475569 !important;
    font-size: 14px !important;
}

.dash-table-container .page-number.current {
    background-color: #2563eb !important;
    color: white !important;
    border-color: #2563eb !important;
}

/* 카드 스타일 */
.stats-card {
    transition: transform 0.3s ease;
    height: 100%;
}

.stats-card:hover {
    transform: translateY(-5px);
}

/* 테이블 호버 효과 */
.dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner tr:hover {
    background-color: #f8fafc !important;
}

/* 스크롤바 스타일링 */
.dash-table-container .dash-spreadsheet-container {
    scrollbar-width: thin;
    scrollbar-color: #cbd5e1 #f8fafc;
}

.dash-table-container .dash-spreadsheet-container::-webkit-scrollbar {
    height: 8px;
    width: 8px;
}

.dash-table-container .dash-spreadsheet-container::-webkit-scrollbar-track {
    background: #f8fafc;
}

.dash-table-container .dash-spreadsheet-container::-webkit-scrollbar-thumb {
    background-color: #cbd5e1;
    border-radius: 4px;
}
'''

app = Dash(
    __name__,
    external_stylesheets=[
        'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
    ],
    suppress_callback_exceptions=True
)

app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>배송 모니터링 시스템</title>
        {{%css%}}
        <style>
            {custom_style}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    create_navbar(),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', className='container-fluid page-container')
], className='min-vh-100 bg-light')


# 페이지 라우팅
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/delivery':
        return delivery_page.create_delivery_page()
    elif pathname == '/driver':
        return driver_page.create_driver_page()
    return main_page.create_main_page()


# 메인 페이지 실시간 업데이트
@app.callback(
    Output('main-delivery-table', 'data'),
    Input('main-interval-component', 'n_intervals')
)
def update_main_page_data(n):
    df = dg.generate_delivery_data()
    # ETA를 datetime으로 변환하여 정렬
    df['ETA_datetime'] = pd.to_datetime(df['ETA'])
    df = df.sort_values('ETA_datetime')
    df = df.drop('ETA_datetime', axis=1)
    # 상위 5개만 반환
    return df.head(5).to_dict('records')


# 배송 테이블 업데이트
@app.callback(
    Output('delivery-table', 'data', allow_duplicate=True),
    [Input('delivery-table', 'page_current'),
     Input('delivery-table', 'page_size'),
     Input('delivery-refresh', 'n_clicks'),
     Input('delivery-search-btn', 'n_clicks'),
     Input('delivery-search', 'n_submit')],
    [State('delivery-search', 'value')],
    prevent_initial_call=True
)
def update_delivery_table(page_current, page_size, n_clicks, search_clicks, search_submit, search_value):
    df = dg.generate_delivery_data()

    if search_value:
        df = dg.search_dataframe(df, search_value)

    start = page_current * page_size if page_current is not None else 0
    end = (page_current + 1) * page_size if page_current is not None else page_size
    return df.iloc[start:end].to_dict('records')


# 드라이버 테이블 업데이트
@app.callback(
    Output('driver-table', 'data', allow_duplicate=True),
    [Input('driver-table', 'page_current'),
     Input('driver-table', 'page_size'),
     Input('driver-refresh', 'n_clicks'),
     Input('driver-search-btn', 'n_clicks'),
     Input('driver-search', 'n_submit')],
    [State('driver-search', 'value')],
    prevent_initial_call=True
)
def update_driver_table(page_current, page_size, n_clicks, search_clicks, search_submit, search_value):
    df = dg.generate_driver_data()

    if search_value:
        df = dg.search_dataframe(df, search_value)

    start = page_current * page_size if page_current is not None else 0
    end = (page_current + 1) * page_size if page_current is not None else page_size
    return df.iloc[start:end].to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)