# src/routes/dash_routes.py
from flask import Blueprint, jsonify, request
from src.service.dashboard_service import DashboardService
from werkzeug.exceptions import BadRequest
import logging

logger = logging.getLogger(__name__)


def init_routes(service: DashboardService = None):
    if service is None:
        service = DashboardService()

    routes = Blueprint('dash_routes', __name__)
    BASE_PATH = '/api/dashboard'

    @routes.route(f'{BASE_PATH}/data', methods=['GET'])
    def get_dashboard_data():
        """대시보드 데이터 조회 API"""
        try:
            # URL 파라미터로 필터값과 페이지 정보 받기
            filters = {
                'department': request.args.get('department'),
                'status': request.args.get('status'),
                'driver': request.args.get('driver'),
                'search': request.args.get('search')
            }

            # 페이지네이션 파라미터
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 15))

            logger.info(f"Fetching dashboard data with filters: {filters}, page: {page}, page_size: {page_size}")

            data = service.get_dashboard_data(page=page, page_size=page_size)
            logger.info(f"Retrieved {len(data.get('data', []))} records")

            return jsonify({
                'status': 'success',
                'data': data
            }), 200
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @routes.route(f'{BASE_PATH}/status', methods=['PUT'])
    def update_status():
        """배송 상태 업데이트 API"""
        try:
            data = request.get_json()
            logger.info(f"Updating status with data: {data}")

            if not data or 'delivery_id' not in data or 'new_status' not in data:
                logger.error("Missing required fields")
                raise BadRequest('delivery_id and new_status are required')

            success = service.update_delivery_status(
                delivery_id=data['delivery_id'],
                new_status=data['new_status']
            )

            if success:
                logger.info("Status update successful")
                return jsonify({
                    'status': 'success',
                    'message': 'Status updated successfully'
                }), 200
            else:
                logger.error("Status update failed")
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to update status'
                }), 400

        except BadRequest as e:
            logger.error(f"Bad request: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return jsonify({
                'status': 'error',
                'message': f"Update failed: {str(e)}"
            }), 500

    @routes.route(f'{BASE_PATH}/driver/assign', methods=['POST'])
    def assign_driver():
        """기사 할당 API"""
        try:
            data = request.get_json()
            logger.info(f"Assigning driver with data: {data}")

            if not data or 'delivery_ids' not in data or 'driver_id' not in data:
                logger.error("Missing required fields")
                raise BadRequest('delivery_ids and driver_id are required')

            success = service.assign_driver(
                delivery_ids=data['delivery_ids'],
                driver_id=data['driver_id']
            )

            if success:
                logger.info("Driver assignment successful")
                return jsonify({
                    'status': 'success',
                    'message': 'Driver assigned successfully'
                }), 200
            else:
                logger.error("Driver assignment failed")
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to assign driver'
                }), 400

        except BadRequest as e:
            logger.error(f"Bad request: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Error assigning driver: {e}")
            return jsonify({
                'status': 'error',
                'message': f"Assignment failed: {str(e)}"
            }), 500

    @routes.route(f'{BASE_PATH}/drivers', methods=['GET'])
    def get_drivers():
        """기사 목록 조회 API"""
        try:
            logger.info("Fetching drivers list")
            drivers = service.get_drivers()
            logger.info(f"Retrieved {len(drivers)} drivers")

            return jsonify({
                'status': 'success',
                'message': 'Drivers retrieved successfully',
                'drivers': drivers
            }), 200
        except Exception as e:
            logger.error(f"Error fetching drivers: {e}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to retrieve drivers: {str(e)}"
            }), 500

    @routes.route(f'{BASE_PATH}/health', methods=['GET'])
    def health_check():
        """시스템 상태 확인 API"""
        try:
            # 서비스를 통해 데이터베이스 연결 상태 확인
            service.health_check()
            return jsonify({
                'status': 'success',
                'message': 'System is healthy'
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'error',
                'message': 'System health check failed'
            }), 500

    return routes
