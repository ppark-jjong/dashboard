from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DashboardDelivery(BaseModel):
    """대시보드에서 사용할 배송 정보"""
    id: int
    department: str
    type: str
    driver: Optional[str] = None
    dps: str = Field(..., min_length=10, max_length=20)
    sla: str
    eta: datetime
    status: str
    address: str
    recipient: str
    reason: Optional[str] = None

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    """상태 업데이트 요청"""
    delivery_id: int
    new_status: str

class DriverAssignment(BaseModel):
    """기사 할당 요청"""
    delivery_ids: list[int]
    driver_id: str