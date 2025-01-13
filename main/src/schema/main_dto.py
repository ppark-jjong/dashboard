# src/schemas/main_dto.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }

# Request Models
class FilterParams(BaseModel):
    department: Optional[str] = None
    status: Optional[str] = None
    driver: Optional[str] = None
    search: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(15, ge=1, le=100)

class StatusUpdateRequest(BaseModel):
    delivery_id: str = Field(..., example="DPS123")
    new_status: str = Field(..., example="대기")

class DriverAssignRequest(BaseModel):
    delivery_ids: List[str] = Field(..., example=["DPS123", "DPS124"])
    driver_id: str = Field(..., example="DRV001")

# Response Models
class DriverResponse(BaseSchema):
    driver: int
    driver_name: str
    driver_contact: str
    driver_region: str

class DashboardItemResponse(BaseSchema):
    type: str
    dps: str
    status: str
    driver: Optional[DriverResponse]
    postal_code: str
    address: str
    customer: str
    contact: Optional[str]
    remark: Optional[str]
    eta: Optional[datetime]
    depart_time: Optional[datetime]
    completed_time: Optional[datetime]

class DashboardDataResponse(BaseSchema):
    data: List[DashboardItemResponse]
    total_records: int
    total_pages: int
    current_page: int
    page_size: int
    has_next: bool
    has_prev: bool

class StatusUpdateResponse(BaseSchema):
    message: str
    delivery_id: str
    updated_status: str

class DriverAssignResponse(BaseSchema):
    message: str
    assigned_count: int
    driver_id: str

class DriversListResponse(BaseSchema):
    drivers: List[DriverResponse]
    message: str