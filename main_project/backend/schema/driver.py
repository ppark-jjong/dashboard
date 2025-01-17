from pydantic import BaseModel
from typing import List

"""
GET /api/drivers 응답
{
  "drivers": [
    {
      "id": "D123",
      "name": "홍길동"
    }
  ]
}"""


class Driver(BaseModel):
    id: int
    name: str


class DriverResponse(BaseModel):
    drivers: List[Driver]


"""
POST /api/assignDriver 요청/응답
요청: {
  "driver_id": "D123",
  "dpsList": ["DPS123", "DPS124"]
}
응답: {
  "success": true
}
"""


class DriverAssignmentRequest(BaseModel):
    driver_id: int
    dpsList: List[str]


class DriverAssignmentResponse(BaseModel):
    success: bool
    assignedCount: int
    message: Optional[str] = None
