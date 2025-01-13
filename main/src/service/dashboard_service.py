import logging
from typing import Optional, List, Dict
from src.repository.mysql_repository import MySQLRepository
from src.schema.main_dto import (
    FilterParams, StatusUpdateRequest, DriverAssignRequest,
    DashboardDataResponse, StatusUpdateResponse, DriverAssignResponse,
    DriversListResponse, DashboardItemResponse
)

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self, mysql_repo: Optional[MySQLRepository] = None):
        self.repository = mysql_repo or MySQLRepository()

    def refresh_dashboard(self) -> bool:
        """대시보드 데이터 새로고침"""
        try:
            logger.info("Refreshing dashboard data...")
            success = self.repository.update_dashboard_data()
            if not success:
                raise ValueError("Dashboard data refresh failed")
            logger.info("Dashboard data refreshed successfully.")
            return True
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
            raise

    def get_dashboard_data(self, filters: FilterParams) -> DashboardDataResponse:
        """대시보드 데이터 조회"""
        try:
            skip = (filters.page - 1) * filters.page_size
            items, total_count = self.repository.get_dashboard_items(
                skip=skip,
                limit=filters.page_size,
                filters=filters.dict(exclude_none=True)
            )

            total_pages = (total_count + filters.page_size - 1) // filters.page_size

            dashboard_items = [DashboardItemResponse.from_orm(item) for item in items]

            return DashboardDataResponse(
                data=dashboard_items,
                total_records=total_count,
                total_pages=total_pages,
                current_page=filters.page,
                page_size=filters.page_size,
                has_next=filters.page < total_pages,
                has_prev=filters.page > 1
            )
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise

    def update_delivery_status(self, request: StatusUpdateRequest) -> StatusUpdateResponse:
        """배송 상태 업데이트"""
        try:
            current_item = self.repository.get_dashboard_items(
                skip=0, limit=1, filters={"dps": request.delivery_id}
            )[0][0]
            if not current_item:
                raise ValueError(f"No item found with ID {request.delivery_id}")

            success = self.repository.update_status(
                delivery_id=request.delivery_id,
                new_status=request.new_status,
                current_status=current_item.status
            )

            if not success:
                raise ValueError(f"Failed to update status for delivery {request.delivery_id}")

            return StatusUpdateResponse(
                message="Status updated successfully",
                delivery_id=request.delivery_id,
                updated_status=request.new_status
            )
        except Exception as e:
            logger.error(f"Error updating delivery status: {e}")
            raise

    def assign_driver(self, request: DriverAssignRequest) -> DriverAssignResponse:
        """기사 할당"""
        try:
            if not request.delivery_ids:
                raise ValueError("No delivery IDs provided")

            success = self.repository.assign_driver(
                delivery_ids=request.delivery_ids,
                driver_id=request.driver_id
            )

            if not success:
                raise ValueError(f"Failed to assign driver {request.driver_id}")

            return DriverAssignResponse(
                message="Driver assigned successfully",
                assigned_count=len(request.delivery_ids),
                driver_id=request.driver_id
            )
        except Exception as e:
            logger.error(f"Error assigning driver: {e}")
            raise

    def get_drivers(self) -> DriversListResponse:
        """기사 목록 조회"""
        try:
            drivers = self.repository.get_drivers()
            return DriversListResponse(
                drivers=drivers,
                message="Drivers retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting drivers: {e}")
            raise