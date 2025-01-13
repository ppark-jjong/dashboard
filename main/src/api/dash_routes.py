from flask import Blueprint, jsonify, request
from src.service.dashboard_service import DashboardService
from src.schema.main_dto import FilterParams, StatusUpdateRequest, DriverAssignRequest
from werkzeug.exceptions import BadRequest
import logging

logger = logging.getLogger(__name__)

service = DashboardService()

def init_routes(service: DashboardService):
    routes = Blueprint('dash_routes', __name__, url_prefix='/api/dashboard')

    @routes.route('/refresh', methods=['POST'])
    def refresh_dashboard():
        try:
            service.refresh_dashboard()
            return jsonify({'status': 'success', 'message': 'Dashboard refreshed.'}), 200
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @routes.route('/data', methods=['GET'])
    def get_dashboard_data():
        try:
            filters = FilterParams(
                department=request.args.get('department'),
                status=request.args.get('status'),
                driver=request.args.get('driver'),
                search=request.args.get('search'),
                page=int(request.args.get('page', 1)),
                page_size=int(request.args.get('page_size', 15))
            )
            response_data = service.get_dashboard_data(filters)
            return jsonify({'status': 'success', 'data': response_data.dict()}), 200
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @routes.route('/status', methods=['PUT'])
    def update_status():
        try:
            data = request.get_json()
            if not data or 'delivery_id' not in data or 'new_status' not in data:
                raise BadRequest('delivery_id and new_status are required')
            request_data = StatusUpdateRequest(**data)
            response = service.update_delivery_status(request_data)
            return jsonify({'status': 'success', 'data': response.dict()}), 200
        except BadRequest as e:
            logger.error(f"Bad request: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @routes.route('/driver/assign', methods=['POST'])
    def assign_driver():
        try:
            data = request.get_json()
            if not data or 'delivery_ids' not in data or 'driver_id' not in data:
                raise BadRequest('delivery_ids and driver_id are required')
            request_data = DriverAssignRequest(**data)
            response = service.assign_driver(request_data)
            return jsonify({'status': 'success', 'data': response.dict()}), 200
        except BadRequest as e:
            logger.error(f"Bad request: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            logger.error(f"Error assigning driver: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @routes.route('/drivers', methods=['GET'])
    def get_drivers():
        try:
            response = service.get_drivers()
            return jsonify({'status': 'success', 'data': response.dict()}), 200
        except Exception as e:
            logger.error(f"Error fetching drivers: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return routes
