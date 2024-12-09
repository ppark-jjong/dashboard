from fastapi import APIRouter, HTTPException
from servicetest import get_redis_data, insert_data_to_redis
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# 라우터 생성
router = APIRouter()

@router.get("/ping")
async def ping():
    """헬스체크 API"""
    return {"message": "pong"}

@router.get("/get-data")
async def fetch_data():
    """Redis에서 데이터 조회"""
    try:
        data = get_redis_data()
        logging.info(f"데이터 조회 성공: {len(data)}개의 레코드 반환")
        return data  # "data" 키 없이 배열만 반환
    except Exception as e:
        logging.error(f"데이터 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="데이터 조회 실패")

@router.post("/refresh-data")
async def refresh_data():
    """Redis에 데이터 새로 삽입"""
    try:
        insert_data_to_redis()
        logging.info("Redis 데이터 새로 삽입 완료")
        return {"message": "데이터가 성공적으로 새로고침되었습니다."}
    except Exception as e:
        logging.error(f"데이터 새로고침 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="데이터 새로고침 실패")
