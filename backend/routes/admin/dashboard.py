from flask import Blueprint, jsonify, request
from services import AdminService, ConfigService, StatisticsService
from utils.jwt import token_required, role_required
from utils.api_response import mark_legacy_route

admin_dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/api/admin')


@admin_dashboard_bp.route('/dashboard/stats', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def dashboard_stats():
    result = AdminService.get_dashboard_stats()
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_dashboard_bp.route('/dashboard/trend', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def dashboard_trend():
    days = request.args.get('days', 7, type=int)
    result = StatisticsService.get_attendance_trend(days=days)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_dashboard_bp.route('/config', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def get_config():
    config = ConfigService.get_punch_config()
    return jsonify({'code': 200, 'message': 'success', 'data': config}), 200


@admin_dashboard_bp.route('/config', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_config():
    data = request.get_json()
    result = ConfigService.update_punch_config(data)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_dashboard_bp.route('/punch-location', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def get_punch_location():
    result = AdminService.get_punch_location()
    response = jsonify({
        'code': 200, 'message': 'success',
        'data': {'location': result.get('data'), 'compatibility': result.get('compatibility')}
    })
    response.status_code = 200
    return mark_legacy_route(response)


@admin_dashboard_bp.route('/punch-location', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def set_punch_location():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius = data.get('radius')
    enabled = data.get('enabled', 1)

    result = AdminService.save_punch_location(name, latitude, longitude, radius, enabled)
    response = jsonify({'code': 200, 'message': 'success', 'data': result})
    response.status_code = 200
    return mark_legacy_route(response)
