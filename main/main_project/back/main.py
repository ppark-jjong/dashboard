# main.py
from fastapi import FastAPI
from api.main_routes import router as dashboard_router

def create_app():
    app = FastAPI()
    # /api 경로 아래로 dashboard 라우터를 붙인다
    app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # uvicorn main:app --reload 로 실행 가능
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
