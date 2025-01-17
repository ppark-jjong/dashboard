from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

"""
GET /api/dashboard 응답을 위한 모델들
테이블 데이터 조회 시 사용

{
  "totalCount": 100,
  "data": [{
    "dps": "DPS123",
    "department": "물류팀",
    "type": "일반배송",
    ...
  }]
}
"""


class DeliveryBase(BaseModel):
    dps: str
    department: str
    type: str
    warehouse: str
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None
    status: str  # "대기", "진행", "완료", "이슈"
    sla: str
    eta: str
    city: str
    region: str
    district: str
    address: str
    postal_code: str
    customer: str
    contact: str
    duration_time: int
    depart_time: Optional[str] = None
    completed_time: Optional[str] = None
    remark: Optional[str] = None


class DeliveryResponse(BaseModel):
    totalCount: int
    data: List[DeliveryBase]
