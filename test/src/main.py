from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from servicetest import insert_data_to_redis
from apitest import router as api_router
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# FastAPI 애플리케이션 초기화
app = FastAPI()

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../template")

# API 라우터 추가
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 Redis 초기 데이터 삽입"""
    logging.info("Redis 초기 데이터를 삽입합니다.")
    insert_data_to_redis()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """대시보드 렌더링"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    logging.info("서버를 시작합니다.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
