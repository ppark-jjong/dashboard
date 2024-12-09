from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from servicetest import insert_data_to_redis

import redis
import logging

# Redis 설정
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

app = FastAPI()

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")


# Redis 데이터 가져오기 함수
def get_redis_data():
    keys = redis_client.keys("delivery:*")
    data = [redis_client.hgetall(key) for key in keys]
    logging.info(f"Redis에서 {len(data)}개의 데이터를 성공적으로 불러왔습니다.")
    return data


@app.get("/")
async def serve_index(request):
    """HTML 템플릿 반환"""
    return templates.TemplateResponse("index.html", {"request": request})


def refresh_data_dash(n_clicks):
    if ctx.triggered_id == "refresh-button":
        logging.info("사용자가 새로고침 버튼을 클릭했습니다.")
        insert_data_to_redis()
    return get_redis_data()


def create_dashboard():
    return app
