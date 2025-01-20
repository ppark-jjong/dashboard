# backend/api/main_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import aioredis
from typing import List
from schema.dashboard_schema import DriverResponse
from model.main_model import Driver


from schema.dashboard_schema import (
    DashboardParams,
    DashboardResponse,
    DashboardDetail,
    DriverAssignRequest,
    StatusUpdateRequest,
    BaseResponse,
)
from service.dashboard_service import DashboardService
from util.database_util import get_db, get_redis

router = APIRouter(tags=["dashboard"])


def get_dashboard_service(
    db: Session = Depends(get_db), redis: aioredis.Redis = Depends(get_redis)
) -> DashboardService:
    return DashboardService(db, redis)


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_list(
    params: DashboardParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardResponse:
    """대시보드 목록 조회"""
    try:
        return await service.get_dashboard_items(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assignDriver", response_model=BaseResponse)
async def assign_driver(
    request: DriverAssignRequest,
    service: DashboardService = Depends(get_dashboard_service),
) -> BaseResponse:
    """기사 할당"""
    try:
        success = await service.assign_driver(request.driver_id, request.dpsList)
        if success:
            return BaseResponse(
                success=True,
                message=f"{len(request.dpsList)}건의 작업이 할당되었습니다.",
            )
        return BaseResponse(success=False, message="기사 할당에 실패했습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/dashboard/{dps}/status", response_model=BaseResponse)
async def update_status(
    dps: str,
    request: StatusUpdateRequest,
    service: DashboardService = Depends(get_dashboard_service),
) -> BaseResponse:
    """작업 상태 업데이트"""
    try:
        if request.new_status not in ["대기", "진행", "완료", "이슈"]:
            raise HTTPException(status_code=400, detail="잘못된 상태값입니다.")

        success = await service.update_status(dps, request.new_status)
        if success:
            return BaseResponse(
                success=True,
                message=f"상태가 {request.new_status}(으)로 변경되었습니다.",
            )
        return BaseResponse(success=False, message="상태 변경에 실패했습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{dps}/detail", response_model=DashboardDetail)
async def get_dashboard_detail(
    dps: str, service: DashboardService = Depends(get_dashboard_service)
) -> DashboardDetail:
    """작업 상세 정보 조회"""
    try:
        detail = await service.get_dashboard_detail(dps)
        if not detail:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
        return detail
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drivers", tags=["drivers"])
async def get_drivers(db: Session = Depends(get_db)):
    """기사 목록 조회"""
    try:
        drivers = db.query(Driver).all()
        return [
            {
                "driver": d.driver,
                "driver_name": d.driver_name,
                "driver_contact": d.driver_contact,
                "driver_region": d.driver_region,
            }
            for d in drivers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
