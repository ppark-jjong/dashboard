# main_routes.py
from fastapi import APIRouter, Query, HTTPException, Path
from typing import Optional
import json
from repository.redis_repository import RedisRepository
from schema.delivery import DeliveryListParams, DeliveryResponse
from schema.driver import DriverAssignmentRequest, DriverAssignmentResponse
from schema.status import StatusUpdateRequest, StatusUpdateResponse

router = APIRouter()


@router.get("/dashboard", response_model=DeliveryResponse)
async def get_dashboard_list(
    status: Optional[str] = Query(None, description="상태 필터"),
    driver_id: Optional[int] = Query(None, description="기사 ID 필터"),
    search: Optional[str] = Query(None, description="검색어"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(15, ge=1, le=100, description="페이지당 항목 수"),
):
    """
    Redis에서 'dashboard:*' 키들을 가져와 필터링 및 페이지네이션 처리
    """
    repo = RedisRepository()
    keys = repo.redis_client.keys("dashboard:*")
    data_list = []

    for key in keys:
        item_str = repo.redis_client.get(key)
        if not item_str:
            continue
        item = json.loads(item_str)

        # 필터 적용
        if status and item.get("status") != status:
            continue
        if driver_id and item.get("driver_id") != driver_id:
            continue
        if search:
            search_lower = search.lower()
            # 검색어가 dps, 고객명, 주소, 연락처 등에 포함되어 있는지 확인
            if not any(
                search_lower in str(item.get(field, "")).lower()
                for field in ["dps", "customer", "address", "contact"]
            ):
                continue

        data_list.append(item)

    # 페이지네이션
    total_count = len(data_list)
    total_pages = (total_count + limit - 1) // limit
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    return {
        "totalCount": total_count,
        "data": data_list[start_idx:end_idx],
        "currentPage": page,
        "totalPages": total_pages,
    }


@router.get("/drivers")
async def get_drivers():
    """기사 목록 조회"""
    repo = RedisRepository()
    # 중복없는 driver_id, driver_name 추출
    keys = repo.redis_client.keys("dashboard:*")
    driver_dict = {}

    for key in keys:
        item_str = repo.redis_client.get(key)
        if not item_str:
            continue
        item = json.loads(item_str)
        d_id = item.get("driver_id")
        d_name = item.get("driver_name")
        if d_id and d_name:
            driver_dict[d_id] = d_name

    drivers = [{"id": k, "name": v} for k, v in driver_dict.items()]
    return {"drivers": drivers}


@router.post("/assignDriver", response_model=DriverAssignmentResponse)
async def assign_driver(request: DriverAssignmentRequest):
    """선택된 배송건들에 기사 할당"""
    repo = RedisRepository()
    assigned_count = 0

    # 기사 존재 여부 확인
    driver_exists = False
    drivers_response = await get_drivers()
    for driver in drivers_response["drivers"]:
        if driver["id"] == request.driver_id:
            driver_exists = True
            break

    if not driver_exists:
        raise HTTPException(status_code=404, detail="Driver not found")

    keys = repo.redis_client.keys("dashboard:*")
    for key in keys:
        item_str = repo.redis_client.get(key)
        if not item_str:
            continue
        item = json.loads(item_str)

        if item.get("dps") in request.dpsList and item.get("status") == "대기":
            # 기사 할당 및 상태 업데이트
            item["driver_id"] = request.driver_id
            item["driver_name"] = (
                f"기사{request.driver_id}"  # 실제로는 기사 정보 조회 필요
            )
            item["status"] = "진행"
            item["depart_time"] = str(datetime.now())

            repo.redis_client.set(key, json.dumps(item, ensure_ascii=False))
            assigned_count += 1

    if assigned_count == 0:
        return {
            "success": False,
            "assignedCount": 0,
            "message": "할당 가능한 배송건이 없습니다.",
        }

    return {
        "success": True,
        "assignedCount": assigned_count,
        "message": f"{assigned_count}건이 할당되었습니다.",
    }


@router.put("/dashboard/{item_id}/status", response_model=StatusUpdateResponse)
async def update_status(
    item_id: int = Path(..., description="배송건 ID"),
    request: StatusUpdateRequest = None,
):
    """배송 상태 업데이트"""
    if request.new_status not in ["대기", "진행", "완료", "이슈"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    repo = RedisRepository()
    key = f"dashboard:{item_id}"
    item_str = repo.redis_client.get(key)

    if not item_str:
        raise HTTPException(status_code=404, detail="Item not found")

    item = json.loads(item_str)
    old_status = item.get("status")

    # 상태 업데이트 및 시간 정보 갱신
    item["status"] = request.new_status
    if request.new_status == "진행" and old_status == "대기":
        item["depart_time"] = str(datetime.now())
    elif request.new_status in ["완료", "이슈"] and old_status == "진행":
        item["completed_time"] = str(datetime.now())

    repo.redis_client.set(key, json.dumps(item, ensure_ascii=False))

    return {"success": True, "item": item, "message": "상태가 업데이트되었습니다."}
