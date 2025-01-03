from flask import Blueprint, jsonify, request
from src.service.dashboard_service import DashboardService
from werkzeug.exceptions import BadRequest

def init_routes(service: DashboardService):
    routes = Blueprint('dash_routes', __name__)

    @routes.route('/api/sync', methods=['POST'])
    def sync_data():
        """데이터 동기화 API - 새로고침 버튼 클릭 시 호출"""
        try:
            success = service.sync_data()  # 동기 방식으로 변경
            if success:
                return jsonify({'status': 'success'})
            return jsonify({'status': 'error'}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': f"Sync failed: {str(e)}"}), 500

    @routes.route('/api/status', methods=['PUT'])
    def update_status():
        """배송 상태 업데이트 API - Redis만 업데이트"""
        data = request.get_json()
        if not data or 'delivery_id' not in data or 'new_status' not in data:
            raise BadRequest('Invalid payload: delivery_id and new_status are required.')

        try:
            success = service.update_delivery_status(data['delivery_id'], data['new_status'])
            if success:
                return jsonify({'status': 'success'})
            return jsonify({'status': 'error', 'message': 'Failed to update status'}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': f"Update failed: {str(e)}"}), 500

    @routes.route('/api/driver/assign', methods=['POST'])
    def assign_driver():
        """기사 할당 API - Redis만 업데이트"""
        data = request.get_json()
        if not data or 'delivery_ids' not in data or 'driver_id' not in data:
            raise BadRequest('Invalid payload: delivery_ids and driver_id are required.')

        try:
            success = service.assign_driver(data['delivery_ids'], data['driver_id'])
            if success:
                return jsonify({'status': 'success'})
            return jsonify({'status': 'error', 'message': 'Failed to assign driver'}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': f"Assignment failed: {str(e)}"}), 500

    return routes
