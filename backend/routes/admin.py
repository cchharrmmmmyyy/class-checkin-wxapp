"""
管理员路由模块
提供管理员用户管理、考勤管理、配置管理等功能的接口
"""
from flask import Blueprint, jsonify, request, send_file
from services import AdminService, ConfigService
from utils.auth import token_required, role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required(['admin'])
def get_users():
    """
    获取用户列表（支持分页、筛选）
    ---
    查询参数: class_name, role, page, size
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    class_name = request.args.get('class_name', '').strip() or None
    role = request.args.get('role', '').strip() or None
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    users = AdminService.list_users()

    if class_name:
        users = [u for u in users if u.get('class') == class_name]
    if role:
        users = [u for u in users if u.get('role') == role]

    total = len(users)
    start = (page - 1) * size
    end = start + size
    paginated_users = users[start:end]

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'users': paginated_users,
            'total': total,
            'page': page,
            'size': size
        }
    }), 200


@admin_bp.route('/users', methods=['POST'])
@token_required
@role_required(['admin'])
def create_user():
    """
    创建用户
    ---
    请求体: {"username": "xxx", "user_id": "xxx", "password": "xxx", "role": "xxx", "class": "xxx"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    data = request.get_json()
    username = data.get('username', '').strip()
    user_id = data.get('user_id', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip()
    class_name = data.get('class', '').strip()

    if not username or not user_id or not password or not role:
        return jsonify({
            'code': 5000,
            'message': '用户名、密码、角色和用户ID不能为空'
        }), 400

    result = AdminService.save_user(username, user_id, password, role, class_name)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_user(user_id):
    """
    更新用户信息
    ---
    请求体: {"username": "xxx", "role": "xxx", "class": "xxx", "password": "xxx"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip()
    class_name = data.get('class', '').strip()

    result = AdminService.save_user(username, user_id, password, role, class_name)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_user(user_id):
    """
    删除用户（软删除）
    ---
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    result = AdminService.delete_user(user_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/users/reset-password', methods=['POST'])
@token_required
@role_required(['admin'])
def admin_reset_password():
    """
    重置用户密码（管理员操作）
    ---
    请求体: {"user_id": "xxx"}
    返回: {"code": 200, "message": "success", "data": {"new_password": "xxx"}}
    """
    data = request.get_json()
    user_id = data.get('user_id', '').strip()

    if not user_id:
        return jsonify({
            'code': 5000,
            'message': '用户ID不能为空'
        }), 400

    result = AdminService.reset_password(user_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/attendance-records', methods=['GET'])
@token_required
@role_required(['admin'])
def get_attendance_records():
    """
    获取考勤记录
    ---
    查询参数: username, user_id, start_date, end_date, leave_status
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    username = request.args.get('username', '').strip() or None
    user_id = request.args.get('user_id', '').strip() or None
    start_date = request.args.get('start_date', '').strip() or None
    end_date = request.args.get('end_date', '').strip() or None
    leave_status = request.args.get('leave_status', '').strip() or None

    records = AdminService.get_attendance_records(
        username=username,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        leave_status=leave_status
    )
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': records
    }), 200


@admin_bp.route('/attendance-records', methods=['POST'])
@token_required
@role_required(['admin'])
def create_attendance_record():
    """
    创建或更新考勤记录
    ---
    请求体: {"id": null, "user_id": "xxx", "punch_date": "xxx", ...}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    data = request.get_json()
    record_id = data.get('id', '').strip() or None
    user_id = data.get('user_id', '').strip()
    punch_date = data.get('punch_date', '').strip() or None
    leave_start_date = data.get('leave_start_date', '') or None
    leave_end_date = data.get('leave_end_date', '') or None
    leave_status = data.get('leave_status', 'pending').strip()

    if not user_id:
        return jsonify({
            'code': 5000,
            'message': '用户ID不能为空'
        }), 400

    result = AdminService.save_attendance_record(
        record_id, user_id, punch_date,
        leave_start_date, leave_end_date, leave_status
    )
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/attendance-records/<int:record_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_attendance_record(record_id):
    """
    删除考勤记录
    ---
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    result = AdminService.delete_attendance_record(record_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/punch-location', methods=['GET'])
@token_required
@role_required(['admin'])
def get_punch_location():
    """
    获取打卡位置配置
    ---
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    result = AdminService.get_punch_location()
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result.get('data')
    }), 200


@admin_bp.route('/punch-location', methods=['POST'])
@token_required
@role_required(['admin'])
def set_punch_location():
    """
    设置打卡位置
    ---
    请求体: {"name": "xxx", "latitude": 1.0, "longitude": 1.0, "radius": 100, "enabled": 1}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    data = request.get_json()
    name = data.get('name', '').strip()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius = data.get('radius')
    enabled = data.get('enabled', 1)

    result = AdminService.save_punch_location(name, latitude, longitude, radius, enabled)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/config', methods=['GET'])
@token_required
@role_required(['admin'])
def get_config():
    """
    获取全局配置
    ---
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    config = ConfigService.get_punch_config()
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': config
    }), 200


@admin_bp.route('/config', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_config():
    """
    更新全局配置
    ---
    请求体: {"global_time_check_enabled": true, ...}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    data = request.get_json()
    result = ConfigService.update_punch_config(data)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200