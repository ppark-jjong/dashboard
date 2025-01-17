from pydantic import BaseModel

"""
PUT /api/dashboard/{dps_id}/status
요청: {
  "status": "진행"
}
응답: {
  "success": true
}
"""


class StatusUpdateRequest(BaseModel):
    status: str


class StatusUpdateResponse(BaseModel):
    success: bool
