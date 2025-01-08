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
            data = service.get_dashboard_data()
            return jsonify({
                'status': 'success',
                'data': data
            }), 200
        except Exception as e:
            logger.error(f"데이터 조회 실패: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @routes.route(f'{BASE_PATH}/status', methods=['PUT'])
    def update_status():
        """배송 상태 업데이트 API"""
        try:
            data = request.get_json()
            if not data or 'delivery_id' not in data or 'new_status' not in data:
                raise BadRequest('delivery_id and new_status are required')

            success = service.update_delivery_status(
                delivery_id=data['delivery_id'],
                new_status=data['new_status']
            )

            if success:
                return jsonify({
                    'status': 'success',
                    'message': 'Status updated successfully'
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to update status'
                }), 400

        except BadRequest as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"상태 업데이트 실패: {e}")
            return jsonify({
                'status': 'error',
                'message': f"Update failed: {str(e)}"
            }), 500

    @routes.route(f'{BASE_PATH}/driver/assign', methods=['POST'])
    def assign_driver():
        """기사 할당 API"""
        try:
            data = request.get_json()
            if not data or 'delivery_ids' not in data or 'driver_id' not in data:
                raise BadRequest('delivery_ids and driver_id are required')

            success = service.assign_driver(
                delivery_ids=data['delivery_ids'],
                driver_id=data['driver_id']
            )

            if success:
                return jsonify({
                    'status': 'success',
                    'message': 'Driver assigned successfully'
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to assign driver'
                }), 400

        except BadRequest as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"기사 할당 실패: {e}")
            return jsonify({
                'status': 'error',
                'message': f"Assignment failed: {str(e)}"
            }), 500

    @routes.route(f'{BASE_PATH}/drivers', methods=['GET'])
    def get_drivers():
        """기사 목록 조회 API"""
        try:
            drivers = service.get_drivers()
            return jsonify({
                'status': 'success',
                'message': 'Drivers retrieved successfully',
                'drivers': drivers
            }), 200
        except Exception as e:
            logger.error(f"기사 목록 조회 실패: {e}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to retrieve drivers: {str(e)}"
            }), 500

    return routes
