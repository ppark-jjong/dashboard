# app.py
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from components import create_navbar  # 이 부분 추가
import main_page
import delivery_page
import dispatch_page

app = Dash(
    __name__,
    external_stylesheets=[
        'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
    ],
    suppress_callback_exceptions=True
)

app.title = '배송 모니터링 시스템'

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>배송 모니터링 시스템</title>
        {%css%}
        <!-- Bootstrap & jQuery -->
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // 모달 관련 JavaScript 초기화
            document.addEventListener('DOMContentLoaded', function() {
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.target.classList.contains('show')) {
                            const modalElement = mutation.target;
                            const modal = new bootstrap.Modal(modalElement);
                            modal.show();
                        }
                    });
                });

                const modals = document.querySelectorAll('.modal');
                modals.forEach(function(modal) {
                    observer.observe(modal, { attributes: true, attributeFilter: ['class'] });
                });
            });
        </script>
    </body>
</html>
'''

app.layout = html.Div([
    create_navbar(),  # 네비게이션 바 추가
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', className='container-fluid p-4')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/delivery':
        return delivery_page.create_delivery_page()
    elif pathname == '/dispatch':
        return dispatch_page.create_dispatch_page()
    return main_page.create_main_page()

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)