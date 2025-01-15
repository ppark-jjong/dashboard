# back/api/main_routes.py
from fastapi import APIRouter, Query
from typing import Optional
import json
from back.repository.redis_repository import RedisRepository

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_list(
    status: Optional[str] = Query(None, description="상태 필터"),
    driver_id: Optional[int] = Query(None, description="기사 ID 필터")
):
    """
    Redis에서 'dashboard:*' 키들을 전부 가져와, status/driver_id로 필터 후 반환.
    """
    repo = RedisRepository()
    keys = repo.redis_client.keys("dashboard:*")
    data_list = []

    for key in keys:
        item_str = repo.redis_client.get(key)
        if not item_str:
            continue
        item = json.loads(item_str)

        # 필터 적용 (status, driver_id)
        if status and item.get("status") != status:
            continue
        if driver_id and item.get("driver_id") != driver_id:
            continue

        data_list.append(item)

    # totalCount, data 형식으로 반환
    return {
        "totalCount": len(data_list),
        "data": data_list
    }

@router.get("/drivers")
def get_drivers():
    """
    기사 목록만 따로 반환하는 예시.
    실제로는 별도 키를 써서 관리하거나, 
    dashboard:* 데이터에서 driver_id/driver_name만 중복없이 추출할 수도 있음.
    """
    repo = RedisRepository()
    # 간단 예: dashboard:*에서 driver_id와 driver_name을 추출
    keys = repo.redis_client.keys("dashboard:*")
    driver_set = {}
    for key in keys:
        item_str = repo.redis_client.get(key)
        if not item_str:
            continue
        item = json.loads(item_str)
        d_id = item.get("driver_id")
        d_name = item.get("driver_name")
        if d_id and d_name:
            driver_set[d_id] = d_name

    drivers = [{"id": k, "name": v} for k, v in driver_set.items()]
    return {"drivers": drivers}


@router.post("/assignDriver")
def assign_driver(dpsList: list[str], driver_id: int):
    """
    선택된 여러건(dpsList)을 '대기' 상태에서 '진행'으로 변경 + 기사 정보 업데이트
    예: body = { "driver_id": 101, "dpsList": ["9545123456", ...] }
    """
    repo = RedisRepository()
    assigned_count = 0

    # Redis에서 dashboard:* 전부 뒤져서 dps가 매칭되는 아이템을 업데이트
    keys = repo.redis_client.keys("dashboard:*")

    for key in keys:
        item_str = repo.redis_client.get(key)
        if not item_str:
            continue
        item = json.loads(item_str)
        
        if item.get("dps") in dpsList and item.get("status") == "대기":
            # 기사 배정
            item["driver_id"] = driver_id
            # driver_name은 실제 driver 목록에서 찾아도 되고, 여기선 임시로
            item["driver_name"] = f"기사{driver_id}"
            item["status"] = "진행"
            # depart_time 등도 업데이트 가능
            item["depart_time"] = str("2025-01-15 10:00:00")

            # Redis에 다시 저장
            repo.redis_client.set(key, json.dumps(item, ensure_ascii=False))
            assigned_count += 1

    return {
        "success": assigned_count > 0,
        "assignedCount": assigned_count
    }


@router.put("/dashboard/{item_id}/status")
def update_status(item_id: int, new_status: str):
    """
    /dashboard/1/status?new_status=완료 
    또는 body JSON: { "new_status": "완료" }
    
    Redis에서 dashboard:<item_id>를 찾아 상태 변경
    """
    repo = RedisRepository()
    key = f"dashboard:{item_id}"
    item_str = repo.redis_client.get(key)
    if not item_str:
        return {"success": False, "message": "Item not found"}

    item = json.loads(item_str)
    old_status = item.get("status")

    # 상태에 따라 depart_time, completed_time 업데이트 가능
    item["status"] = new_status
    if new_status == "진행" and old_status == "대기":
        item["depart_time"] = str(datetime.now())
    elif new_status in ["완료", "이슈"] and old_status == "진행":
        item["completed_time"] = str(datetime.now())

    repo.redis_client.set(key, json.dumps(item, ensure_ascii=False))

    return {
        "success": True,
        "item": item
    }
