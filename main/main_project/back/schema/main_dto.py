from typing import Optional, List, Union
from datetime import datetime, date
from pydantic import BaseModel, Field

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else None,
            date: lambda v: v.strftime("%Y-%m-%d") if v else None
        }

# Common Response Models
class DriverResponse(BaseSchema):
    driver: int
    driver_name: str
    driver_contact: str
    driver_region: str

class PostalCodeResponse(BaseSchema):
    postal_code: str
    duration_time: Optional[int]
    distance: Optional[int]
    city: Optional[str]
    district: Optional[str]

# Dashboard Models
class DashboardBase(BaseSchema):
    type: str = Field(..., description="작업 유형 (delivery/return)")
    dps: str = Field(..., description="작업 번호")
    status: str = Field(default="대기", description="작업 상태")
    department: str = Field(..., description="담당 부서")
    postal_code: str = Field(..., description="우편번호")
    address: str = Field(..., description="주소")
    customer: str = Field(..., description="고객명")
    contact: Optional[str] = Field(None, description="연락처")
    remark: Optional[str] = Field(None, description="비고")
    eta: Optional[datetime] = Field(None, description="도착예정시간")

class DeliveryDashboardResponse(DashboardBase):
    warehouse: Optional[str]
    sla: Optional[str]
    dispatch_time: Optional[datetime]
    delivery_id: str
    driver: Optional[DriverResponse]
    postal_code_info: Optional[PostalCodeResponse]

class ReturnDashboardResponse(DashboardBase):
    package_type: Optional[str]
    qty: Optional[int]
    dispatch_date: Optional[date]
    return_id: str
    driver: Optional[DriverResponse]
    postal_code_info: Optional[PostalCodeResponse]

class DashboardResponse(BaseSchema):
    id: int
    task: Union[DeliveryDashboardResponse, ReturnDashboardResponse]

# Request Models
class FilterParams(BaseModel):
    department: Optional[str] = None
    status: Optional[str] = None
    driver: Optional[int] = None
    search: Optional[str] = None
    task_type: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(15, ge=1, le=100)

class StatusUpdateRequest(BaseModel):
    task_id: int = Field(..., description="Dashboard task ID")
    new_status: str = Field(..., description="New status value")

class DriverAssignRequest(BaseModel):
    task_ids: List[int] = Field(..., description="Dashboard task IDs")
    driver_id: int = Field(..., description="Driver ID to assign")

# Response Models
class DashboardDataResponse(BaseSchema):
    data: List[DashboardResponse]
    total_records: int
    total_pages: int
    current_page: int
    page_size: int
    has_next: bool
    has_prev: bool

class StatusUpdateResponse(BaseSchema):
    message: str
    task_id: int
    updated_status: str

class DriverAssignResponse(BaseSchema):
    message: str
    assigned_count: int
    driver_id: int

class DriversListResponse(BaseSchema):
    drivers: List[DriverResponse]
    message: str = "Drivers retrieved successfully"