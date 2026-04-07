from flask import Blueprint, request, jsonify
from services import AdminService
from utils.auth import token_required, role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required('admin')
def get_all_users():
    return jsonify({
        'success': True,
        'data': AdminService.list_users()
    }), 200


@admin_bp.route('/users', methods=['POST'])
@token_required
@role_required('admin')
def add_or_update_user():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip()
    class_name = data.get('class', '').strip()
    user_id = data.get('user_id', '').strip()

    if not username or not password or not role or not user_id:
        return jsonify({
            'success': False,
            'message': '用户名、密码、角色和用户ID不能为空',
            'code': 5000
        }), 400

    return jsonify(AdminService.save_user(username, user_id, password, role, class_name)), 200


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_user(user_id):
    return jsonify(AdminService.delete_user(user_id)), 200


@admin_bp.route('/attendance-records', methods=['GET'])
@token_required
@role_required('admin')
def get_attendance_records():
    username = request.args.get('username', '').strip() or None
    user_id = request.args.get('user_id', '').strip() or None
    start_date = request.args.get('start_date', '').strip() or None
    end_date = request.args.get('end_date', '').strip() or None
    leave_status = request.args.get('leave_status', '').strip() or None

    records = AdminService.get_attendance_records(
        username=username, user_id=user_id,
        start_date=start_date, end_date=end_date,
        leave_status=leave_status
    )

    return jsonify({'success': True, 'data': records}), 200


@admin_bp.route('/attendance-records', methods=['POST'])
@token_required
@role_required('admin')
def add_or_update_attendance_record():
    data = request.get_json()
    record_id = data.get('id', '').strip()
    user_id = data.get('user_id', '').strip()
    punch_date = data.get('punch_date', '').strip() or None
    leave_start_date = data.get('leave_start_date', '') or None
    leave_end_date = data.get('leave_end_date', '') or None
    leave_status = data.get('leave_status', 'pending').strip()

    if not user_id:
        return jsonify({
            'success': False,
            'message': '用户ID不能为空',
            'code': 5000
        }), 400

    return jsonify(AdminService.save_attendance_record(
        record_id, user_id, punch_date,
        leave_start_date, leave_end_date, leave_status
    )), 200


@admin_bp.route('/attendance-records/<int:record_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_attendance_record(record_id):
    return jsonify(AdminService.delete_attendance_record(record_id)), 200


@admin_bp.route('/punch-location', methods=['GET'])
@token_required
@role_required('admin')
def get_punch_location():
    return jsonify(AdminService.get_punch_location()), 200


@admin_bp.route('/punch-location', methods=['POST'])
@token_required
@role_required('admin')
def set_punch_location():
    data = request.get_json()
    name = data.get('name', '').strip()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius = data.get('radius')
    enabled = data.get('enabled', 1)

    return jsonify(AdminService.save_punch_location(name, latitude, longitude, radius, enabled)), 200


@admin_bp.route('/reset-password', methods=['POST'])
@token_required
@role_required('admin')
def reset_password():
    data = request.get_json()
    user_id = data.get('user_id', '').strip()

    if not user_id:
        return jsonify({
            'success': False,
            'message': '用户ID不能为空',
            'code': 5000
        }), 400

    return jsonify(AdminService.reset_password(user_id)), 200
