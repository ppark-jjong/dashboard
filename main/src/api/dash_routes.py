from flask import Blueprint, jsonify, request
from src.service.dashboard_service import DashboardService
from werkzeug.exceptions import BadRequest


def init_routes(service: DashboardService):
    routes = Blueprint('dash_routes', __name__)

    # 기본 API 경로
    BASE_PATH = '/api/dashboard'

    @routes.route(f'{BASE_PATH}/sync', methods=['GET', 'POST'])
    def sync_data():
        """데이터 동기화 API - 새로고침 버튼 클릭 시 호출"""
        try:
            success = service.sync_data()
            return jsonify({
                'status': 'success' if success else 'error',
                'message': 'Data synchronized successfully' if success else 'Sync failed'
            }), 200 if success else 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f"Sync failed: {str(e)}"
            }), 500

    @routes.route(f'{BASE_PATH}/status', methods=['PUT'])
    def update_status():
        """배송 상태 업데이트 API - Redis만 업데이트"""
        try:
            data = request.get_json()
            if not data or 'delivery_id' not in data or 'new_status' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid payload: delivery_id and new_status are required'
                }), 400

            success = service.update_delivery_status(data['delivery_id'], data['new_status'])
            return jsonify({
                'status': 'success' if success else 'error',
                'message': 'Status updated successfully' if success else 'Failed to update status'
            }), 200 if success else 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f"Update failed: {str(e)}"
            }), 500

    @routes.route(f'{BASE_PATH}/driver/assign', methods=['POST'])
    def assign_driver():
        """기사 할당 API - Redis만 업데이트"""
        try:
            data = request.get_json()
            if not data or 'delivery_ids' not in data or 'driver_id' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid payload: delivery_ids and driver_id are required'
                }), 400

            success = service.assign_driver(data['delivery_ids'], data['driver_id'])
            return jsonify({
                'status': 'success' if success else 'error',
                'message': 'Driver assigned successfully' if success else 'Failed to assign driver'
            }), 200 if success else 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f"Assignment failed: {str(e)}"
            }), 500

    return routes