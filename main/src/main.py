from flask import Flask
from src.routes.dash_routes import init_dash_apps

# Flask 애플리케이션 생성
app = Flask(
    __name__,
    static_folder="src/dash_views/static",  # static 폴더 경로 설정
    static_url_path="/static"              # 정적 파일 URL 경로 설정
)

# Dash 애플리케이션 초기화
dash_apps = init_dash_apps(app)

@app.route("/")
def home():
    return """
    <h1>Flask와 Dash 통합 테스트</h1>
    <ul>
        <li><a href="/main/">메인 페이지</a></li>
        <li><a href="/delivery/">배송 현황 페이지</a></li>
        <li><a href="/driver/">기사 현황 페이지</a></li>
    </ul>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
