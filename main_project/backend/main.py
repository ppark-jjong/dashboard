# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.main_routes import router as dashboard_router
from repository.load_mock_data import load_mock_data_to_redis


def create_app():
    app = FastAPI()
    app.include_router(dashboard_router, prefix="/", tags=["dashboard"])

    @app.on_event("startup")
    async def startup_event():
        # 서버 시작 시 mock 데이터 로드
        load_mock_data_to_redis()

    return app


app = create_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

if __name__ == "__main__":
    import uvicorn

    # uvicorn main:app --reload 로 실행 가능
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
