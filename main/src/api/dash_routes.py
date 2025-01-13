# src/api/dash_routes.py
from flask import Blueprint, jsonify, request
from src.service.dashboard_service import DashboardService
from src.schema.main_dto import FilterParams
from werkzeug.exceptions import BadRequest
import logging

logger = logging.getLogger(__name__)


def init_routes(service: DashboardService):
    api_routes = Blueprint('api', __name__, url_prefix='/api')  # 기본 URL 접두사를 /api로 설정

    @api_routes.route('/dashboard/refresh', methods=['POST'])
    def refresh_dashboard():
        """대시보드 데이터 새로고침"""
        try:
            success = service.refresh_dashboard()
            if success:
                return jsonify({
                    'status': 'success',
                    'message': 'Dashboard refreshed successfully'
                }), 200
            return jsonify({
                'status': 'error',
                'message': 'Failed to refresh dashboard'
            }), 500
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @api_routes.route('/dashboard/data', methods=['GET'])
    def get_dashboard_data():
        """대시보드 데이터 조회"""
        try:
            filters = FilterParams(
                department=request.args.get('department'),
                status=request.args.get('status'),
                driver=request.args.get('driver'),
                search=request.args.get('search'),
                page=int(request.args.get('page', 1)),
                page_size=int(request.args.get('page_size', 15))
            )
            response = service.get_dashboard_data(filters)
            return jsonify({
                'status': 'success',
                'data': response.dict()
            }), 200
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @api_routes.route('/dashboard/status', methods=['PUT'])
    def update_status():
        """상태 업데이트"""
        try:
            data = request.get_json()
            if not data or 'dps' not in data or 'new_status' not in data:
                raise BadRequest('dps and new_status are required')

            response = service.update_status(
                dps=data['dps'],
                new_status=data['new_status']
            )
            return jsonify({
                'status': 'success',
                'data': response.dict()
            }), 200
        except BadRequest as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @api_routes.route('/dashboard/driver/assign', methods=['POST'])
    def assign_driver():
        """기사 할당"""
        try:
            data = request.get_json()
            if not data or 'dps_list' not in data or 'driver_id' not in data:
                raise BadRequest('dps_list and driver_id are required')

            response = service.assign_driver(
                dps_list=data['dps_list'],
                driver_id=data['driver_id']
            )
            return jsonify({
                'status': 'success',
                'data': response.dict()
            }), 200
        except BadRequest as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Error assigning driver: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @api_routes.route('/dashboard/detail/<dps>', methods=['GET'])
    def get_detail_data(dps):
        """상세 정보 조회"""
        try:
            response = service.get_detail_data(dps)
            return jsonify({
                'status': 'success',
                'data': response
            }), 200
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 404
        except Exception as e:
            logger.error(f"Error fetching detail data: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @api_routes.route('/dashboard/drivers', methods=['GET'])
    def get_drivers():
        """기사 목록 조회"""
        try:
            response = service.get_drivers()
            return jsonify({
                'status': 'success',
                'data': response.dict()
            }), 200
        except Exception as e:
            logger.error(f"Error fetching drivers: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    return api_routes