from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Request Schemas
class DashboardParams(BaseModel):
    status: Optional[str] = None
    driver_id: Optional[int] = None
    search: Optional[str] = None
    page: int = Field(default=1, gt=0)
    limit: int = Field(default=15, gt=0, le=100)

class DriverAssignRequest(BaseModel):
    driver_id: int
    dpsList: List[str]

class StatusUpdateRequest(BaseModel):
    new_status: str

# Response Schemas
class DriverResponse(BaseModel):
    driver: int
    driver_name: str
    driver_contact: str
    driver_region: str

    class Config:
        from_attributes = True

class DriversResponse(BaseModel):
    drivers: List[DriverResponse]

class DashboardItem(BaseModel):
    type: str
    status: str
    driver_id: Optional[int] = None
    driver_name: Optional[str] = None
    department: str
    postal_code: str
    region: Optional[str] = None
    duration_time: Optional[int] = None
    address: str
    customer: str
    contact: Optional[str] = None
    remark: Optional[str] = None
    eta: Optional[datetime] = None
    depart_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    driver_contact: Optional[str] = None
    sla: Optional[str] = None
    warehouse: Optional[str] = None
    dps: str

class DashboardResponse(BaseModel):
    totalCount: int
    data: List[DashboardItem]
    currentPage: int
    totalPages: int

class DashboardDetail(BaseModel):
    type: str
    status: str
    driver_id: Optional[int] = None
    driver_name: Optional[str] = None
    department: str
    postal_code: str
    region: Optional[str] = None
    duration_time: Optional[int] = None
    address: str
    customer: str
    contact: Optional[str] = None
    remark: Optional[str] = None
    eta: Optional[datetime] = None
    depart_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    driver_contact: Optional[str] = None
    sla: Optional[str] = None
    warehouse: Optional[str] = None
    dps: str
    dispatch_time: Optional[datetime] = None
    package_type: Optional[str] = None
    qty: Optional[int] = None
    dispatch_date: Optional[datetime] = None

class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None